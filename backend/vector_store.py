import os
import json
import math
import re
import numpy as np
import requests
import logging

logger = logging.getLogger("vector_store")

def get_ollama_embedding(text, model="nomic-embed-text:latest"):
    """Get embedding from local Ollama service, handling API version variations."""
    # Clean text to ensure it's not empty
    text = text.strip()
    if not text:
        text = "empty"
        
    # Attempt newer /api/embed endpoint
    try:
        resp = requests.post("http://localhost:11434/api/embed", json={
            "model": model,
            "input": text
        }, timeout=10)
        if resp.status_code == 200:
            embeddings = resp.json().get("embeddings")
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
    except Exception:
        pass
        
    # Fallback to older /api/embeddings endpoint
    try:
        resp = requests.post("http://localhost:11434/api/embeddings", json={
            "model": model,
            "prompt": text
        }, timeout=10)
        if resp.status_code == 200:
            embedding = resp.json().get("embedding")
            if embedding:
                return embedding
    except Exception as e:
        logger.warning(f"Failed to generate embedding via Ollama: {e}")
        
    # Final fallback: return zero vector so index doesn't fail
    return [0.0] * 768

def cosine_similarity(v1, v2):
    """Compute cosine similarity between two lists/arrays."""
    a = np.array(v1)
    b = np.array(v2)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))

class BM25Index:
    """A clean, dependency-free implementation of the BM25 retrieval algorithm."""
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = 0
        self.avg_doc_len = 0.0
        self.doc_lens = []
        self.doc_term_freqs = [] # list of dicts: term -> count
        self.df = {} # term -> doc count
        self.idf = {} # term -> idf score

    def tokenize(self, text):
        """Lowercase and tokenize text into words, removing basic punctuation."""
        return re.findall(r'\w+', text.lower())

    def fit(self, corpus_texts):
        """Fit BM25 parameters on a list of document strings."""
        self.doc_count = len(corpus_texts)
        if self.doc_count == 0:
            return
            
        self.doc_lens = []
        self.doc_term_freqs = []
        self.df = {}
        total_len = 0
        
        for text in corpus_texts:
            tokens = self.tokenize(text)
            self.doc_lens.append(len(tokens))
            total_len += len(tokens)
            
            # Count frequencies
            term_freq = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
            self.doc_term_freqs.append(term_freq)
            
            # Update document frequency (seen once per doc)
            for token in term_freq.keys():
                self.df[token] = self.df.get(token, 0) + 1
                
        self.avg_doc_len = total_len / self.doc_count if self.doc_count > 0 else 0.0
        
        # Calculate IDF for each term
        for term, doc_freq in self.df.items():
            # BM25 IDF formula with smoothing
            self.idf[term] = math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)

    def get_scores(self, query):
        """Return BM25 scores for all documents given a query string."""
        query_tokens = self.tokenize(query)
        scores = [0.0] * self.doc_count
        
        for idx in range(self.doc_count):
            doc_len = self.doc_lens[idx]
            term_freqs = self.doc_term_freqs[idx]
            score = 0.0
            
            for token in query_tokens:
                if token in term_freqs:
                    freq = term_freqs[token]
                    idf = self.idf.get(token, 0.0)
                    # BM25 formula numerator/denominator
                    num = freq * (self.k1 + 1)
                    denom = freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += idf * (num / denom)
            scores[idx] = score
            
        return scores

class HybridStore:
    def __init__(self, persist_dir="data"):
        self.persist_dir = persist_dir
        self.db_file = os.path.join(persist_dir, "rag_store.json")
        self.chunks = []       # list of dicts (all chunk details)
        self.embeddings = []   # list of float lists (1-to-1 matching chunks)
        self.bm25 = BM25Index()
        self.sources = set()   # set of file/url names already ingested
        
        os.makedirs(self.persist_dir, exist_ok=True)
        self.load()

    def save(self):
        """Persist index to disk."""
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings,
            "sources": list(self.sources)
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(self.chunks)} chunks to {self.db_file}")

    def load(self):
        """Load index from disk and re-initialize BM25 corpus."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", [])
                    self.embeddings = data.get("embeddings", [])
                    self.sources = set(data.get("sources", []))
                
                # Re-fit BM25
                corpus = [c["text"] for c in self.chunks]
                self.bm25.fit(corpus)
                logger.info(f"Loaded {len(self.chunks)} chunks from {self.db_file}")
            except Exception as e:
                logger.error(f"Failed to load RAG store: {e}")
                self.chunks = []
                self.embeddings = []
                self.sources = set()

    def clear(self):
        """Clear the store."""
        self.chunks = []
        self.embeddings = []
        self.sources = set()
        self.bm25 = BM25Index()
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def add_document(self, doc_data):
        """Add parsed document chunks, generate embeddings, and update BM25."""
        source = doc_data["source"]
        
        # Avoid duplicate ingestion
        if source in self.sources:
            logger.info(f"Document '{source}' already indexed. Skipping.")
            return False

        doc_chunks = doc_data["chunks"]
        logger.info(f"Adding document: {source} ({len(doc_chunks)} chunks)")
        
        new_chunks = []
        new_embeddings = []
        
        for idx, chunk in enumerate(doc_chunks):
            # Format to unified shape
            unified_chunk = {
                "chunk_id": chunk.get("chunk_id", f"{source}_chunk_{idx}"),
                "text": chunk["text"],
                "type": chunk.get("type", "paragraph"),
                "metadata": {
                    "heading": chunk.get("metadata", {}).get("heading", ""),
                    "timestamp": chunk.get("metadata", {}).get("timestamp", ""),
                    "source": source,
                    "source_type": doc_data["source_type"]
                }
            }
            new_chunks.append(unified_chunk)
            
            # Generate embedding
            emb = get_ollama_embedding(chunk["text"])
            new_embeddings.append(emb)
            
        self.chunks.extend(new_chunks)
        self.embeddings.extend(new_embeddings)
        self.sources.add(source)
        
        # Fit BM25 on all chunks
        corpus = [c["text"] for c in self.chunks]
        self.bm25.fit(corpus)
        
        # Save updates
        self.save()
        return True

    def search(self, query, top_k=5, mode="hybrid"):
        """Execute hybrid search using Reciprocal Rank Fusion (RRF)."""
        if not self.chunks:
            return []

        # 1. Vector Search
        query_emb = get_ollama_embedding(query)
        vector_scores = []
        for idx, emb in enumerate(self.embeddings):
            sim = cosine_similarity(query_emb, emb)
            vector_scores.append((idx, sim))
            
        # Rank by vector score descending
        vector_ranked = sorted(vector_scores, key=lambda x: x[1], reverse=True)
        
        # 2. BM25 Search
        bm25_scores = self.bm25.get_scores(query)
        bm25_ranked = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)
        
        # 3. Blend ranks using Reciprocal Rank Fusion (RRF)
        # RRF formula: Score(d) = sum( 1 / (60 + Rank_m(d)) )
        k_rrf = 60
        rrf_scores = {}
        
        # Assign ranks
        for rank, (idx, _) in enumerate(vector_ranked):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k_rrf + rank + 1))
            
        for rank, (idx, _) in enumerate(bm25_ranked):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (k_rrf + rank + 1))
            
        # Optional document type priority (boost factors)
        # Boost specific document types if helpful, or keep it standard
        
        # Sort chunks by final RRF score
        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        results = []
        for rank, idx in enumerate(sorted_indices[:top_k]):
            chunk = self.chunks[idx].copy()
            # Attach ranking details for debugging/UI
            chunk["rrf_score"] = rrf_scores[idx]
            chunk["vector_score"] = dict(vector_scores)[idx]
            chunk["bm25_score"] = bm25_scores[idx]
            chunk["rank"] = rank + 1
            results.append(chunk)
            
        return results
