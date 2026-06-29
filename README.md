# 🚀 MoniRAG – Multi-Modal Retrieval-Augmented Generation Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange)
![Groq](https://img.shields.io/badge/Groq-Fallback-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# 📖 Executive Summary

MoniRAG is a modular Retrieval-Augmented Generation (RAG) platform that enables intelligent question answering over both uploaded documents and crawled websites. The system combines document parsing, recursive web crawling, semantic chunking, vector-based retrieval, and hybrid Large Language Model (LLM) inference to provide grounded, context-aware responses.

Unlike traditional chatbots that rely solely on pretrained knowledge, MoniRAG builds a local knowledge base from user-provided content. Documents are parsed into structured text, divided into semantic chunks, converted into embeddings, and stored in a persistent vector store. User queries are matched against these embeddings to retrieve the most relevant context before being passed to the language model.

The application adopts a hybrid inference strategy by prioritizing local generation through Ollama while automatically falling back to Groq Cloud if the local model is unavailable or times out. This approach ensures high availability, reduced latency, and improved reliability.

MoniRAG is designed for educational use, research, enterprise knowledge management, document intelligence, and AI-powered search systems.

---

# 📑 Table of Contents

- Executive Summary
- Project Overview
- Problem Statement
- Solution Overview
- Key Features
- Technology Stack
- Software Architecture
- Project Structure
- Core Engine Documentation
- Installation Guide
- Configuration
- API Documentation
- Deployment Guide
- Logging
- Testing
- Troubleshooting
- Security
- Future Roadmap
- License

---

# 🎯 Project Overview

MoniRAG is a FastAPI-based intelligent knowledge retrieval platform capable of processing multiple information sources and answering user questions using Retrieval-Augmented Generation (RAG).

The system supports two major ingestion methods:

- Uploading local documents
- Crawling live websites

Both sources are transformed into searchable knowledge using semantic embeddings. During question answering, the platform retrieves the most relevant information from the indexed knowledge base and generates grounded responses using a hybrid LLM architecture.

The entire pipeline executes locally while optionally supporting cloud-based inference through Groq for enhanced reliability.

---

# ❗ Problem Statement

Large Language Models are powerful but often suffer from several limitations:

- Hallucinated responses
- Lack of organization-specific knowledge
- Inability to access newly uploaded documents
- No understanding of private datasets
- Difficulty handling large document collections

Traditional keyword-based search systems also struggle with semantic understanding, making it difficult to retrieve relevant information from extensive knowledge bases.

---

# 💡 Solution

MoniRAG addresses these challenges by implementing a Retrieval-Augmented Generation pipeline.

The system performs the following operations:

- Accepts user documents and websites
- Extracts meaningful textual information
- Splits content into semantic chunks
- Generates vector embeddings
- Stores vectors locally
- Retrieves the most relevant chunks
- Uses retrieved context to generate accurate answers
- Falls back to Groq Cloud whenever Ollama is unavailable

This architecture minimizes hallucinations while ensuring responses remain grounded in the available knowledge.

---

# ✨ Key Features

## 📄 Multi-Format Document Processing

- PDF parsing
- Microsoft Word (.docx) parsing
- PowerPoint (.pptx) parsing
- Plain text support
- HTML processing
- OCR-ready image handling

---

## 🌐 Recursive Website Crawling

- Crawl public websites
- Configurable crawl depth
- Internal link discovery
- Duplicate content removal
- Automatic text extraction
- Metadata preservation

---

## ✂️ Intelligent Text Chunking

- Automatic document segmentation
- Context-preserving chunk generation
- Optimized retrieval accuracy
- Metadata-aware chunk storage

---

## 🧠 Semantic Vector Search

- Embedding generation
- Persistent vector storage
- Similarity-based retrieval
- Fast semantic search

---

## 🤖 Hybrid Large Language Model

Primary Provider

- Ollama (Local)

Fallback Provider

- Groq Cloud

Automatic provider switching ensures uninterrupted response generation.

---

## ⚡ FastAPI Backend

- REST API
- High-performance asynchronous processing
- Browser-based interface
- Modular backend architecture

---

## 💾 Persistent Knowledge Base

The application stores processed knowledge locally, allowing uploaded documents and crawled websites to remain available even after restarting the server.

---

## 📊 Structured Logging

The application records:

- Upload events
- Crawling operations
- Parsing activities
- Query processing
- Retrieval results
- LLM execution
- Errors and warnings

---

## 🔒 Privacy-First Design

- Local document processing
- Local vector storage
- Local inference using Ollama
- Optional cloud fallback
- User-controlled knowledge base

---

# 🎯 Intended Applications

MoniRAG can be used for:

- Research document analysis
- Resume search systems
- Enterprise knowledge management
- AI-powered document assistants
- Educational question answering
- Internal documentation search
- Website knowledge extraction
- Technical support assistants

---

# ⭐ Highlights

- Hybrid RAG Architecture
- Recursive Website Crawling
- Multi-Document Knowledge Base
- Hybrid Ollama + Groq Inference
- Semantic Search
- Persistent Local Storage
- FastAPI Backend
- Interactive Browser Interface
- Modular Software Design
# 🛠 Technology Stack

MoniRAG is developed using modern open-source technologies that provide scalability, modularity, and efficient AI-powered document retrieval.

| Layer | Technology |
|--------|------------|
| Programming Language | Python 3.10+ |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Frontend | HTML5, CSS3, JavaScript |
| Local LLM | Ollama |
| Cloud LLM | Groq |
| Embedding Model | nomic-embed-text |
| Text Generation Model | mistral |
| Vector Storage | JSON-based Persistent Vector Store |
| Web Crawling | BeautifulSoup4 |
| HTML Parsing | BeautifulSoup |
| PDF Parsing | PyPDF |
| DOCX Parsing | python-docx |
| PPTX Parsing | python-pptx |
| OCR | OpenCV + Pillow |
| HTTP Client | Requests |
| Logging | Python Logging Module |

---

# 🏗 Software Architecture

MoniRAG follows a modular layered architecture that separates document ingestion, indexing, retrieval, and language model inference.

```
                        +-----------------------+
                        |      User Browser     |
                        +----------+------------+
                                   |
                                   |
                         HTTP Request/Response
                                   |
                                   ▼
                        +-----------------------+
                        |     FastAPI Server    |
                        +----------+------------+
                                   |
      ----------------------------------------------------------
      |            |              |              |              |
      ▼            ▼              ▼              ▼              ▼
 Document      Web Crawler    Vector Store    LLM Engine    Static UI
  Parser                                           |
      |                                            |
      |                                            ▼
      |                                   Ollama (Primary)
      |                                            |
      |                                   Groq (Fallback)
      |
      ▼
 Smart Chunker
      |
      ▼
 Embedding Engine
      |
      ▼
 Persistent Vector Store
```

---

# 🧩 Software Modules

The project consists of independent modules that communicate through well-defined interfaces.

| Module | Responsibility |
|---------|----------------|
| Frontend | User Interface |
| Backend API | Handles requests |
| Parser Engine | Extracts text from files |
| Web Crawler | Crawls websites recursively |
| Chunker | Splits documents into chunks |
| Vector Store | Stores semantic embeddings |
| Retriever | Finds relevant chunks |
| LLM Manager | Generates final answer |
| Logger | Tracks system activity |

---

# 📂 High-Level Workflow

```
                Upload Document
                       │
                       ▼
              Document Parser
                       │
                       ▼
               Smart Chunker
                       │
                       ▼
             Embedding Generation
                       │
                       ▼
              Local Vector Store
                       │
──────────────────────────────────────────────
                       │
                 User Question
                       │
                       ▼
               Semantic Retrieval
                       │
                       ▼
             Relevant Text Chunks
                       │
                       ▼
               Prompt Generation
                       │
                       ▼
             Ollama (Primary LLM)
                       │
             Success / Failure
                       │
                       ▼
            Groq Cloud (Fallback)
                       │
                       ▼
              Grounded AI Response
```

---

# 🔄 End-to-End Processing Pipeline

The MoniRAG platform follows an end-to-end Retrieval-Augmented Generation pipeline.

```
User Uploads File
        │
        ▼
File Type Detection
        │
        ▼
Document Parsing
        │
        ▼
Text Cleaning
        │
        ▼
Semantic Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Vector Storage
        │
──────────────────────────────────
        │
User Asks Question
        │
        ▼
Generate Query Embedding
        │
        ▼
Similarity Search
        │
        ▼
Retrieve Top Chunks
        │
        ▼
Prompt Builder
        │
        ▼
Ollama
        │
If Failed
        ▼
Groq
        │
        ▼
Final Answer
```

---

# 🏢 System Components

## 1. User Interface

The frontend provides an intuitive browser-based interface where users can:

- Upload documents
- Crawl websites
- Select indexed sources
- Ask natural language questions
- View generated answers

---

## 2. Backend Server

The FastAPI backend acts as the central controller responsible for:

- Processing API requests
- Coordinating document parsing
- Managing vector storage
- Executing semantic retrieval
- Communicating with language models

---

## 3. Document Processing Layer

This layer converts uploaded files into structured textual information suitable for indexing.

Responsibilities include:

- File validation
- Parsing
- Cleaning
- Metadata extraction

---

## 4. Crawling Layer

The crawler enables ingestion of website content.

Features include:

- Recursive crawling
- Internal link discovery
- Duplicate detection
- Crawl depth limitation
- Content extraction

---

## 5. Indexing Layer

Responsible for transforming textual content into searchable semantic representations.

Operations include:

- Chunk creation
- Embedding generation
- Persistent storage
- Metadata management

---

## 6. Retrieval Layer

This component searches the indexed knowledge base.

It performs:

- Query embedding generation
- Similarity search
- Ranking
- Context retrieval

---

## 7. Language Model Layer

Responsible for answer generation.

Provider hierarchy:

```
Ollama
    │
Success?
    │
 ┌──┴──┐
 │ Yes │────────► Return Answer
 └──┬──┘
    │
    ▼
Groq Cloud
    │
    ▼
Return Answer
```

---

# 🔁 Request Lifecycle

```
Browser

↓

FastAPI

↓

Parser / Crawler

↓

Chunk Generator

↓

Vector Store

↓

Retriever

↓

LLM

↓

Generated Answer

↓

Browser
```

---

# 📦 Data Flow

```
Document

↓

Parser

↓

Chunks

↓

Embeddings

↓

Vector Store

↓

User Query

↓

Retriever

↓

Context

↓

LLM

↓

Answer
```

---

# 🎯 Design Principles

MoniRAG is designed around the following software engineering principles:

### Modular Design

Each subsystem performs a single responsibility.

---

### Scalability

New parsers, embedding models, and LLM providers can be integrated with minimal code changes.

---

### Reliability

Hybrid LLM execution ensures continuous availability through automatic fallback mechanisms.

---

### Maintainability

The project structure separates business logic into dedicated modules, improving readability and maintainability.

---

### Extensibility

Future enhancements such as additional parsers, cloud deployment, authentication, or distributed vector stores can be integrated without redesigning the architecture.

---

# 📈 Key Advantages

- Hybrid AI Architecture
- Local Knowledge Base
- Recursive Website Crawling
- Persistent Vector Storage
- Semantic Search
- Automatic LLM Failover
- Modular Codebase
- FastAPI Performance
- Easy Deployment
- Scalable Design
# 📁 Project Structure

The project follows a modular architecture that separates the user interface, backend services, parsing engine, crawling engine, vector storage, and language model management into independent components.

```
MoniRAG/
│
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── crawler.py               # Recursive web crawler
│   ├── parsers.py               # Multi-format document parser
│   ├── chunker.py               # Intelligent text chunking engine
│   ├── vector_store.py          # Persistent vector storage
│   ├── llm.py                   # Hybrid LLM manager
│   ├── config.py                # Application configuration
│   ├── utils.py                 # Utility functions
│   └── __init__.py
│
├── static/
│   ├── app.js                   # Frontend JavaScript
│   ├── styles.css               # Application styling
│   └── logo.png
│
├── templates/
│   └── index.html               # Main user interface
│
├── data/
│   ├── uploads/                 # Uploaded documents
│   ├── crawled/                 # Crawled website content
│   └── rag_store.json           # Persistent vector database
│
├── requirements.txt
├── run.py
├── README.md
└── LICENSE
```

---

# 🧠 Core Engine Documentation

The MoniRAG platform consists of multiple intelligent software components that work together to create a Retrieval-Augmented Generation (RAG) pipeline.

Each component performs a dedicated task while maintaining loose coupling with the remaining modules.

---

# 📄 Document Processing Engine

The document processing engine is responsible for converting uploaded files into structured textual content suitable for semantic indexing.

The parser automatically identifies the uploaded file type and invokes the appropriate extraction method.

Supported operations include:

- File validation
- Format detection
- Text extraction
- Metadata extraction
- Error handling

After parsing, the extracted content is forwarded to the chunking engine.

---

## Supported File Formats

| File Type | Description |
|------------|-------------|
| PDF | Portable Document Format |
| DOCX | Microsoft Word Documents |
| PPTX | Microsoft PowerPoint Presentations |
| TXT | Plain Text Files |
| HTML | Web Documents |
| Images | OCR-based text extraction |

---

## Parsing Workflow

```
Uploaded File

↓

Detect File Extension

↓

Select Appropriate Parser

↓

Extract Text

↓

Extract Metadata

↓

Clean Content

↓

Forward to Chunking Engine
```

---

# 🌐 Recursive Website Crawling Engine

The crawler enables MoniRAG to build knowledge directly from websites.

Instead of processing only uploaded documents, users can provide a URL that becomes part of the searchable knowledge base.

The crawler recursively visits internal links while respecting the configured crawl depth.

---

## Crawler Features

- Recursive crawling
- Configurable crawl depth
- Internal link traversal
- Duplicate page detection
- HTML cleaning
- Metadata extraction
- Automatic indexing

---

## Crawl Workflow

```
User URL

↓

Validate URL

↓

Download HTML

↓

Extract Text

↓

Extract Internal Links

↓

Depth Check

↓

Visit Child Pages

↓

Generate Chunks

↓

Store in Vector Database
```

---

## Crawl Depth

Depth controls how many levels of internal links the crawler visits.

Example:

Depth = 0

```
Home Page
```

Depth = 1

```
Home

├── About

├── Contact

└── Products
```

Depth = 2

```
Home

├── About
│     ├── Team
│     └── History

├── Products
│     ├── Product A
│     └── Product B
```

Increasing crawl depth expands the searchable knowledge base while increasing indexing time.

---

# ✂ Intelligent Text Chunking Engine

Large Language Models cannot efficiently process extremely large documents.

Therefore, every document is divided into smaller semantic chunks before indexing.

The chunking engine preserves contextual relationships while maintaining manageable chunk sizes.

---

## Responsibilities

- Split long documents
- Preserve semantic meaning
- Reduce overlap
- Improve retrieval accuracy
- Generate metadata for each chunk

---

## Chunk Metadata

Each generated chunk contains metadata including:

- Source document
- File type
- Heading
- Chunk number
- Timestamp (if available)

---

## Chunking Workflow

```
Raw Text

↓

Cleaning

↓

Sentence Detection

↓

Chunk Generation

↓

Metadata Assignment

↓

Vector Embedding
```

---

# 📚 Vector Storage Engine

After chunk generation, semantic embeddings are created and stored inside the local vector database.

The vector store enables efficient similarity search during question answering.

Unlike traditional databases, vector storage compares semantic meaning instead of exact keywords.

---

## Responsibilities

- Store embeddings
- Persist knowledge
- Retrieve similar chunks
- Maintain metadata
- Save indexed documents

---

## Stored Information

Each indexed chunk contains:

- Text
- Embedding
- Source
- File Type
- Chunk ID
- Heading
- Timestamp

---

## Storage Workflow

```
Chunks

↓

Embedding Generation

↓

Vector Creation

↓

Persistent Storage

↓

Ready for Retrieval
```

---

# 🔎 Semantic Retrieval Engine

When a user asks a question, the retrieval engine searches the vector database for semantically similar chunks.

Instead of matching keywords, similarity is measured using vector distance.

This allows the system to retrieve contextually relevant information even when wording differs.

---

## Retrieval Pipeline

```
User Question

↓

Embedding Generation

↓

Vector Search

↓

Similarity Ranking

↓

Top Relevant Chunks

↓

Send to LLM
```

---

## Advantages

- Context-aware search
- Faster retrieval
- Reduced hallucination
- Higher answer accuracy
- Semantic understanding

---

# 🧩 Prompt Construction Engine

The retrieved chunks are combined into a structured prompt before being sent to the language model.

The prompt contains:

- User Question
- Retrieved Context
- System Instructions
- Source Information

This ensures that the generated response remains grounded in the indexed knowledge rather than relying solely on pretrained model knowledge.

---

# 📈 Processing Summary

```
Upload Document
        │
        ▼
Document Parser
        │
        ▼
Text Cleaning
        │
        ▼
Chunk Generator
        │
        ▼
Embedding Engine
        │
        ▼
Vector Database
        │
──────────────────────────────
        │
User Query
        │
        ▼
Retriever
        │
        ▼
Relevant Chunks
        │
        ▼
Prompt Builder
        │
        ▼
LLM Engine
        │
        ▼
Generated Answer
``` 
# 🤖 Hybrid Large Language Model (LLM) Engine

MoniRAG utilizes a hybrid language model architecture designed to maximize availability, performance, and reliability.

Instead of depending on a single provider, the platform intelligently switches between a local Large Language Model and a cloud-based provider whenever required.

The architecture ensures uninterrupted response generation even if the local inference engine becomes unavailable.

---

## Primary Language Model

The primary inference engine is powered by **Ollama**.

Advantages include:

- Fully local execution
- No internet dependency
- Better privacy
- Zero API cost
- Faster local inference after model loading
- Complete user control

The default generation model is:

```
mistral
```

The embedding model used for semantic retrieval is:

```
nomic-embed-text
```

---

## Fallback Language Model

If Ollama is unavailable, times out, or returns an error, the request is automatically redirected to Groq Cloud.

Advantages include:

- High availability
- Fast cloud inference
- Automatic recovery
- Minimal interruption

The default fallback model is:

```
llama-3.3-70b-versatile
```

---

# 🔁 LLM Execution Flow

```
User Question
        │
        ▼
Retrieve Context
        │
        ▼
Generate Prompt
        │
        ▼
Attempt Ollama
        │
   ┌────┴────┐
   │ Success │
   └────┬────┘
        │
        ▼
 Return Answer

        │
        ▼

 Failure

        │
        ▼

Attempt Groq

        │
        ▼

Return Answer
```

---

# 🧠 Prompt Construction

Each request sent to the language model contains three primary components:

## System Prompt

Defines the behavior of the language model.

Example responsibilities include:

- Answer only using provided context
- Avoid hallucinations
- Mention missing information when necessary

---

## Retrieved Context

Contains the most relevant semantic chunks retrieved from the vector database.

Each chunk contains metadata such as:

- Source document
- Heading
- File type
- Timestamp (if available)

---

## User Question

The original question entered by the user.

Example:

```
What skills are mentioned in the uploaded resume?
```

---

# 🔒 Grounded Answer Generation

Unlike traditional chatbots, MoniRAG does not rely solely on pretrained knowledge.

Instead, every response is generated using retrieved context from the indexed knowledge base.

This Retrieval-Augmented Generation approach significantly reduces hallucinations and improves factual consistency.

---

# 📡 REST API

The backend exposes RESTful APIs through FastAPI.

These APIs can be consumed by web applications, desktop software, or third-party systems.

---

## Base URL

```
http://127.0.0.1:8000
```

---

# Available Endpoints

## Home

### GET /

Returns the main web interface.

---

## Upload Document

### POST /api/upload

Uploads a supported document and indexes it into the vector database.

Request:

```
Multipart Form Data
```

Response:

```
Upload Successful
```

---

## Crawl Website

### POST /api/crawl

Starts recursive crawling of a website.

Parameters:

- URL
- Crawl Depth

Response:

```
Website Indexed Successfully
```

---

## Ask Question

### POST /api/query

Queries the indexed knowledge base.

Input:

```
Question
Selected Source
```

Output:

```
Generated Answer
Model Used
Latency
Retrieved Sources
```

---

## List Sources

### GET /api/sources

Returns all indexed documents and crawled websites.

---

## Settings

### GET /api/settings

Returns the current system configuration.

---

# 📤 Installation Guide

## Step 1

Clone the repository.

```bash
git clone <repository-url>
```

---

## Step 2

Navigate into the project directory.

```bash
cd MoniRAG
```

---

## Step 3

Create a virtual environment.

```bash
python -m venv venv
```

---

## Step 4

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Step 5

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Step 6

Install Ollama.

Download and install Ollama from the official website.

---

## Step 7

Download the required models.

```bash
ollama pull mistral
```

```bash
ollama pull nomic-embed-text
```

---

## Step 8

Verify the models.

```bash
ollama list
```

Expected output:

```
mistral

nomic-embed-text
```

---

# ▶ Running the Application

## Start Ollama

```bash
ollama serve
```

---

## Start the FastAPI Server

```bash
uvicorn backend.main:app --reload
```

---

## Open the Application

```
http://127.0.0.1:8000
```

---

# ⚙ Configuration

The application can be configured through the backend configuration file.

Typical configurable options include:

- Default language model
- Embedding model
- Crawl depth
- Upload directory
- Chunk size
- Chunk overlap
- Timeout values
- API settings

---

# 📁 Persistent Storage

The application stores indexed knowledge locally.

Stored data includes:

- Uploaded files
- Crawled pages
- Semantic chunks
- Vector database
- Metadata

Knowledge remains available after restarting the application.

---

# 🌐 Browser Compatibility

The application has been designed for modern browsers.

Supported browsers include:

- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- Brave Browser
- Opera

---

# 📈 Performance Characteristics

Typical workflow:

Upload Document

↓

Text Extraction

↓

Chunk Generation

↓

Embedding Generation

↓

Vector Storage

↓

Semantic Retrieval

↓

LLM Generation

↓

Grounded Answer

Performance depends on:

- Document size
- Crawl depth
- Number of indexed documents
- CPU performance
- Available RAM
- Ollama model size

---

# 📦 Deployment Options

MoniRAG can be deployed as:

- Local Desktop Application
- Research Tool
- Internal Knowledge Portal
- Enterprise Documentation Assistant
- AI Search Engine
- Educational Platform
- Document Intelligence System
- Local AI Assistant

The modular architecture also allows future deployment using Docker, cloud virtual machines, or container orchestration platforms.
# 🧪 Testing Strategy

MoniRAG has been tested across multiple functional modules to ensure reliability, correctness, and system stability. Each major component was verified independently before being integrated into the complete Retrieval-Augmented Generation (RAG) pipeline.

---

# Functional Testing

The following functionalities were validated during testing.

| Module | Test Scenario | Expected Result |
|---------|---------------|-----------------|
| Document Upload | Upload supported documents | File uploaded successfully |
| PDF Parsing | Extract text from PDF | Correct text extracted |
| DOCX Parsing | Read Word document | Correct text extracted |
| PPTX Parsing | Extract slide content | Slide text extracted |
| Website Crawling | Crawl website recursively | Pages indexed successfully |
| Chunk Generation | Split large documents | Context preserved |
| Vector Storage | Save semantic chunks | Data persisted successfully |
| Query Processing | Ask knowledge-based question | Accurate answer generated |
| Ollama Integration | Local inference | Answer generated |
| Groq Fallback | Simulate Ollama failure | Automatic cloud inference |
| Source Listing | Display indexed sources | Correct source list returned |

---

# Integration Testing

Integration testing verified communication between software components.

Integrated modules include:

- Document Parser → Chunk Generator
- Chunk Generator → Vector Store
- Vector Store → Retriever
- Retriever → Prompt Builder
- Prompt Builder → LLM Manager
- FastAPI → Frontend
- Crawler → Indexing Engine

The complete RAG pipeline was tested successfully using uploaded documents and live websites.

---

# Performance Testing

The following observations were made during testing.

### Small Documents

- Fast upload
- Immediate indexing
- Low response latency

---

### Medium Documents

- Stable chunk generation
- Efficient retrieval
- Consistent answer quality

---

### Large Documents

- Increased indexing time
- Stable retrieval
- Memory usage proportional to document size

---

### Website Crawling

Performance depends on:

- Crawl depth
- Number of pages
- Internet speed
- Website complexity

---

# Logging System

MoniRAG implements a centralized logging mechanism that records every major system event.

Examples include:

- Server startup
- File upload
- Document parsing
- Chunk creation
- Website crawling
- Query execution
- LLM inference
- Vector storage updates
- Errors
- Warnings

---

## Sample Log Output

```
INFO: Upload requested

INFO: Parsing PDF document

INFO: Generated 12 chunks

INFO: Added vectors to knowledge base

INFO: Query received

INFO: Retrieved relevant chunks

INFO: Using Ollama

INFO: Response generated successfully
```

---

# Error Handling

The application includes defensive programming practices to ensure graceful failure.

Handled situations include:

- Unsupported document formats
- Empty uploads
- Missing files
- Corrupted documents
- Invalid URLs
- Network failures
- Ollama timeout
- Groq API failure
- Empty search results

Whenever possible, meaningful error messages are returned to the user without crashing the application.

---

# Security Considerations

MoniRAG incorporates several security-focused design principles.

## Input Validation

All uploaded files and URLs are validated before processing.

---

## Local Processing

Documents remain on the user's local machine unless cloud inference is explicitly required.

---

## Controlled Website Crawling

Crawler depth restrictions help prevent excessive resource consumption.

---

## Metadata Isolation

Each indexed chunk stores metadata independently, enabling traceability of retrieved information.

---

## Hybrid Execution

Sensitive documents can be processed locally using Ollama without requiring cloud transmission.

---

# Limitations

The current implementation includes the following limitations.

- Requires Ollama installation for local inference.
- Large crawl depths may increase indexing time.
- OCR accuracy depends on image quality.
- Retrieval quality depends on chunk size and document structure.
- Cloud fallback requires internet connectivity.

These limitations are expected for the current version and can be addressed in future releases.

---

# Future Enhancements

The modular architecture allows several future improvements.

## Planned Features

- User authentication
- Multi-user workspace
- Document versioning
- Role-based access control
- Chat history persistence
- PDF highlighting of retrieved passages
- Streaming LLM responses
- Multiple embedding models
- Additional LLM providers
- Docker deployment
- Kubernetes support
- PostgreSQL metadata storage
- FAISS vector indexing
- Distributed vector databases
- GPU acceleration
- Voice-based question answering
- Real-time website monitoring
- Scheduled web crawling
- Automatic knowledge synchronization

---

# Scalability

MoniRAG has been designed with scalability in mind.

The architecture supports:

- Additional parsers
- New embedding models
- Alternative vector databases
- Cloud deployment
- Microservice migration
- API expansion
- Enterprise integrations

without requiring major architectural changes.

---

# Software Engineering Principles

The project follows widely accepted software engineering practices.

- Modular architecture
- Separation of concerns
- Reusable components
- Maintainable codebase
- Extensible design
- Fault tolerance
- Graceful error handling
- Layered architecture
- RESTful API design

---

# Version Information

| Item | Value |
|------|-------|
| Project Name | MoniRAG |
| Version | 1.0.0 |
| Architecture | Retrieval-Augmented Generation |
| Backend | FastAPI |
| Language | Python |
| Deployment | Local |
| License | MIT |
# 📷 Application Screenshots

The following screenshots illustrate the major functionalities of the MoniRAG platform.

---

## Home Dashboard

> *Insert screenshot here*

**Description**

The dashboard provides a clean interface for interacting with the knowledge base. Users can upload documents, crawl websites, manage indexed sources, and ask natural language questions.

---

## Document Upload

> *Insert screenshot here*

**Description**

Users can upload supported document formats including PDF, DOCX, PPTX, TXT, and HTML. Uploaded documents are automatically parsed, chunked, and indexed into the vector database.

---

## Website Crawling

> *Insert screenshot here*

**Description**

Users can provide a website URL and specify the crawl depth. The crawler recursively indexes internal pages and adds them to the knowledge base.

---

## Question Answering

> *Insert screenshot here*

**Description**

The semantic retrieval engine searches the indexed knowledge base and generates grounded responses using the Hybrid LLM Engine.

---

## Source Management

> *Insert screenshot here*

**Description**

Displays all indexed documents and crawled websites currently available in the knowledge base.

---

## Server Logs

> *Insert screenshot here*

**Description**

Real-time backend logs showing uploads, crawling, indexing, retrieval, and language model execution.

---

# ❓ Frequently Asked Questions (FAQ)

## What is Retrieval-Augmented Generation (RAG)?

Retrieval-Augmented Generation is an AI architecture that retrieves relevant information from a knowledge base before generating an answer. This improves factual accuracy and reduces hallucinations.

---

## Does the application work offline?

Yes.

The system supports fully local execution using Ollama. Internet connectivity is only required when the Groq fallback service is used.

---

## Which language model is used?

Default local model:

```
mistral
```

Fallback cloud model:

```
llama-3.3-70b-versatile
```

---

## Can multiple documents be uploaded?

Yes.

The application supports multiple uploaded documents. All indexed content becomes part of the searchable knowledge base.

---

## Does the crawler visit external websites?

No.

The crawler is designed to follow internal links within the specified domain while respecting the configured crawl depth.

---

## Is the indexed knowledge persistent?

Yes.

The vector database is stored locally, allowing indexed documents and websites to remain available after restarting the application.

---

# 🤝 Contribution Guidelines

Contributions are welcome.

Suggested workflow:

1. Fork the repository.
2. Create a feature branch.
3. Implement improvements.
4. Test all changes.
5. Submit a Pull Request with a clear description.

All contributions should maintain the existing coding standards and project structure.

---

# 🛠 Maintenance

To keep the system running efficiently:

- Regularly update Python dependencies.
- Keep Ollama models up to date.
- Remove unused indexed documents.
- Monitor log files for errors.
- Periodically back up the persistent vector database.

---

# 📚 References

The project is based on concepts from:

- Retrieval-Augmented Generation (RAG)
- Semantic Vector Search
- FastAPI Documentation
- Ollama Documentation
- Groq API Documentation
- BeautifulSoup Documentation
- Python Official Documentation

---

# 📄 License

This project is released under the **MIT License**.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to use, modify, distribute, and publish the software, subject to the conditions specified in the MIT License.

---

# 🙏 Acknowledgements

This project was made possible through the use of several outstanding open-source technologies.

Special thanks to the developers and maintainers of:

- Python
- FastAPI
- Uvicorn
- Ollama
- Groq
- BeautifulSoup
- Requests
- PyPDF
- python-docx
- python-pptx
- OpenCV
- Pillow

Their contributions to the open-source community have enabled the development of intelligent AI-powered software systems.

---

# 📬 Support

For questions, suggestions, bug reports, or feature requests, please open an issue in the project repository.

If using this project for academic purposes, please cite the repository appropriately.

---

# 🎯 Conclusion

MoniRAG demonstrates a complete implementation of a modern Retrieval-Augmented Generation (RAG) platform by integrating document processing, recursive web crawling, semantic indexing, vector-based retrieval, and hybrid Large Language Model inference into a unified system.

The platform enables users to build a searchable knowledge base from both uploaded documents and live websites, ensuring that generated answers remain grounded in the indexed content. By combining local inference through Ollama with automatic Groq cloud fallback, the system achieves both reliability and flexibility while maintaining a privacy-first design.

With its modular architecture, RESTful API, browser-based interface, persistent knowledge storage, and scalable design, MoniRAG provides a strong foundation for document intelligence, enterprise knowledge management, educational assistance, and AI-powered search applications.

The architecture has been intentionally designed for future extensibility, allowing seamless integration of additional parsers, embedding models, vector databases, authentication mechanisms, and deployment platforms.

MoniRAG represents a practical implementation of Retrieval-Augmented Generation and demonstrates how modern AI systems can deliver accurate, context-aware, and trustworthy responses by combining semantic retrieval with advanced language models.

---

<div align="center">

## ⭐ If you found this project useful, consider giving it a star.

**MoniRAG — Multi-Modal Retrieval-Augmented Generation Platform**

*Built with Python, FastAPI, Ollama, and Groq.*

**Version 1.0.0**

</div>