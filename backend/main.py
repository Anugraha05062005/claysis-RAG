import os
import time
import shutil
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Import our custom components
from backend.crawler import WebCrawler
from backend.parsers import UnifiedParser
from backend.chunker import SmartChunker
from backend.vector_store import HybridStore
from backend.llm import LLMManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_server")

app = FastAPI(title="Multi-Modal RAG System", description="API for Multi-Modal RAG Chatbot")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories configuration
UPLOAD_DIR = "data/uploads"
SETTINGS_FILE = "data/settings.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load / Save settings helper
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "groq_api_key": os.getenv("GROQ_API_KEY", ""),
        "ollama_model": "mistral:latest",
        "groq_model": "llama-3.3-70b-versatile"
    }

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

import json

# Initialize settings and RAG modules
current_settings = load_settings()
store = HybridStore()
chunker = SmartChunker()

def get_parser():
    settings = load_settings()
    return UnifiedParser(groq_api_key=settings.get("groq_api_key"))

def get_llm():
    settings = load_settings()
    return LLMManager(
        ollama_model=settings.get("ollama_model", "mistral:latest"),
        groq_api_key=settings.get("groq_api_key", ""),
        groq_model=settings.get("groq_model", "llama-3.3-70b-versatile")
    )

# Models for API
class QueryRequest(BaseModel):
    source: Optional[str] = None
    question: str
    depth: Optional[int] = 2
    mode: Optional[str] = "hybrid"

class CrawlRequest(BaseModel):
    url: str
    depth: int = 2

class SettingsUpdate(BaseModel):
    groq_api_key: Optional[str] = None
    ollama_model: Optional[str] = None
    groq_model: Optional[str] = None

# Endpoints
@app.get("/")
def get_index():
    """Serve the index.html from frontend folder."""
    index_path = os.path.abspath("frontend/index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "error", "message": f"Frontend index.html not found at {index_path}"})

@app.post("/api/crawl")
def run_crawl(req: CrawlRequest):
    """Crawl a website recursively and index its pages."""
    logger.info(f"Crawl requested for URL: {req.url} at depth {req.depth}")
    
    start_time = time.time()
    try:
        # Run crawler
        crawler = WebCrawler(req.url, max_depth=req.depth)
        crawled_pages = crawler.crawl()
        
        if not crawled_pages:
            return {
                "status": "warning",
                "message": "No pages crawled. Check if URL is valid or same-domain rules block access.",
                "indexed_pages": 0,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
            
        new_chunks_count = 0
        pages_indexed = 0
        
        # Process and Chunk pages
        for page in crawled_pages:
            # Chunking
            chunks = chunker.chunk_document(page)
            if chunks:
                page_data = {
                    "source_type": "web",
                    "source": page["source"],
                    "chunks": chunks
                }
                # Add to Vector + BM25 store
                success = store.add_document(page_data)
                if success:
                    new_chunks_count += len(chunks)
                    pages_indexed += 1
                    
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "success",
            "message": f"Successfully crawled and indexed {pages_indexed} pages.",
            "indexed_pages": pages_indexed,
            "new_chunks": new_chunks_count,
            "latency_ms": latency_ms
        }
    except Exception as e:
        logger.error(f"Crawling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload any file (document/image/audio/video) and index it."""
    start_time = time.time()
    logger.info(f"Upload requested for file: {file.filename}")
    
    # Save file to upload directory
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse document
        parser = get_parser()
        parsed_doc = parser.parse_file(file_path)
        
        # Chunk document
        chunks = chunker.chunk_document(parsed_doc)
        
        # Save into Hybrid Vector Store
        doc_data = {
            "source_type": parsed_doc["source_type"],
            "source": file.filename,
            "chunks": chunks
        }
        
        success = store.add_document(doc_data)
        latency_ms = int((time.time() - start_time) * 1000)
        
        if not success:
            return {
                "status": "warning",
                "message": f"File '{file.filename}' has already been indexed.",
                "chunks_count": 0,
                "latency_ms": latency_ms
            }
            
        return {
            "status": "success",
            "message": f"Successfully processed and indexed '{file.filename}'",
            "chunks_count": len(chunks),
            "latency_ms": latency_ms
        }
    except Exception as e:
        logger.error(f"Processing upload failed: {e}", exc_info=True)
        # Clean up file if error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
def query_rag(req: QueryRequest):
    """Query the hybrid RAG system."""
    start_time = time.time()
    logger.info(f"Query requested: '{req.question}' on source '{req.source}'")
    
    # 1. Check if source is a URL that isn't indexed yet. If so, crawl it first!
    if req.source and req.source.startswith(("http://", "https://")):
        normalized_source = req.source.split("?")[0].rstrip("/") # Simple clean
        # Match stored sources
        source_found = any(normalized_source in src for src in store.sources)
        if not source_found:
            logger.info(f"Source URL '{req.source}' not indexed yet. Running dynamic crawl...")
            try:
                crawler = WebCrawler(req.source, max_depth=req.depth or 1)
                pages = crawler.crawl()
                for page in pages:
                    chunks = chunker.chunk_document(page)
                    if chunks:
                        store.add_document({
                            "source_type": "web",
                            "source": page["source"],
                            "chunks": chunks
                        })
            except Exception as e:
                logger.error(f"Dynamic crawl failed: {e}")
                # Don't fail the whole query, just proceed with existing DB
                
    # 2. Search
    # Check if we have documents at all
    if not store.chunks:
        return {
            "answer": "The available knowledge base is empty. Please upload some files or crawl a URL first.",
            "sources": [],
            "latency_ms": int((time.time() - start_time) * 1000)
        }
        
    search_results = store.search(req.question, top_k=5, mode=req.mode)
    
    # Filter search results by source if specified (supports both exact name and substring)
    if req.source and not req.source.startswith(("http://", "https://")):
        search_results = [r for r in search_results if req.source.lower() in r["metadata"]["source"].lower()]
        
    if not search_results:
        # If filtering is too strict or search yielded nothing
        return {
            "answer": "Information not found in the available knowledge base.",
            "sources": [],
            "latency_ms": int((time.time() - start_time) * 1000)
        }

    # 3. Generate Answer
    llm = get_llm()
    answer, llm_provider, latency_ms = llm.generate_answer(req.question, search_results, mode=req.mode)
    
    # Format sources for response payload
    formatted_sources = []
    for r in search_results:
        meta = r["metadata"]
        formatted_sources.append({
            "type": meta.get("source_type", "web"),
            "reference": meta.get("source", "unknown"),
            "chunk_id": r.get("chunk_id", ""),
            "heading": meta.get("heading", ""),
            "timestamp": meta.get("timestamp", ""),
            "text": r["text"] # Send snippet back to UI for transparency
        })
        
    total_latency = int((time.time() - start_time) * 1000)
    
    return {
        "answer": answer,
        "sources": formatted_sources,
        "latency_ms": total_latency,
        "llm_provider": llm_provider
    }

@app.get("/api/sources")
def get_sources():
    """List all ingested sources and their chunk count details."""
    sources_summary = {}
    
    # Compile sources and chunk statistics
    for chunk in store.chunks:
        meta = chunk.get("metadata", {})
        source_name = meta.get("source", "Unknown")
        source_type = meta.get("source_type", "unknown")
        
        if source_name not in sources_summary:
            sources_summary[source_name] = {
                "name": source_name,
                "type": source_type,
                "chunks": 0
            }
        sources_summary[source_name]["chunks"] += 1
        
    return list(sources_summary.values())

@app.post("/api/clear")
def clear_knowledge():
    """Reset the knowledge base."""
    store.clear()
    # Remove files in uploads folder
    for f in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception:
            pass
    return {"status": "success", "message": "Knowledge base reset successfully."}

@app.get("/api/settings")
def get_settings():
    """Fetch current system configuration settings."""
    settings = load_settings()
    # Mask API key for UI safety
    masked_key = ""
    key = settings.get("groq_api_key", "")
    if key:
        masked_key = key[:6] + "..." + key[-4:] if len(key) > 10 else "..."
        
    return {
        "groq_api_key_masked": masked_key,
        "ollama_model": settings.get("ollama_model", "mistral:latest"),
        "groq_model": settings.get("groq_model", "llama-3.3-70b-versatile")
    }

@app.post("/api/settings")
def update_settings(update: SettingsUpdate):
    """Save system configuration parameters."""
    settings = load_settings()
    if update.groq_api_key is not None:
        # Only overwrite if it's not a masked placeholder
        if not update.groq_api_key.startswith("gsk_") and update.groq_api_key != "":
            # Check if user passed a masked key back, ignore it
            if "..." not in update.groq_api_key:
                settings["groq_api_key"] = update.groq_api_key
        else:
            settings["groq_api_key"] = update.groq_api_key
            
    if update.ollama_model is not None:
        settings["ollama_model"] = update.ollama_model
    if update.groq_model is not None:
        settings["groq_model"] = update.groq_model
        
    save_settings(settings)
    return {"status": "success", "message": "Settings updated successfully."}

# Mount static files folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")
