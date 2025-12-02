from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager
from models import SearchRequest, SearchResponse, SearchResult
from html_parser import HTMLParser
from chunker import TextChunker
from vector_store import VectorStore
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from cachetools import TTLCache
import validators
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
html_parser = HTMLParser()
chunker = TextChunker(max_tokens=500, overlap_tokens=50)
vector_store = VectorStore()

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        vector_store.initialize_schema()
        logger.info("✅ Vector store schema initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize schema: {e}")
    
    yield
    
    # Shutdown
    html_parser.close()
    vector_store.close()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Website Content Search",
    description="AI-powered semantic search for website content",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Response cache (1 hour TTL, max 100 items)
response_cache = TTLCache(maxsize=100, ttl=3600)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Website Content Search API is running"}


@app.post("/search", response_model=SearchResponse)
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute per IP
async def search(search_request: SearchRequest, request: Request):
    """
    Main search endpoint with caching and guardrails
    """
    try:
        logger.info(f"🔍 Processing search: URL={search_request.url}, Query={search_request.query}")
        
        # --- Guardrails ---
        
        # 1. Validate URL
        if not validators.url(search_request.url):
            raise HTTPException(status_code=400, detail="Invalid URL format")
            
        # 2. Validate Query Length
        if len(search_request.query) > 200:
            raise HTTPException(status_code=400, detail="Query too long (max 200 chars)")
            
        if len(search_request.query) < 2:
            raise HTTPException(status_code=400, detail="Query too short (min 2 chars)")

        # --- Caching ---
        cache_key = f"{search_request.url}:{search_request.query}"
        if cache_key in response_cache:
            logger.info("⚡ Returning cached result")
            return response_cache[cache_key]

        # --- Processing ---
        
        # Step 1: Fetch HTML
        logger.info("📥 Fetching HTML...")
        html_content = await html_parser.fetch_html(search_request.url)
        
        # Step 2: Clean and parse
        logger.info("🧹 Cleaning HTML...")
        soup = html_parser.clean_html(html_content)
        
        # Step 3: Extract content chunks with DOM paths
        logger.info("📄 Extracting content...")
        html_chunks = html_parser.extract_content_chunks(soup)
        
        if not html_chunks:
            raise HTTPException(
                status_code=422,
                detail="No content found on the page. Please try a different URL."
            )
        
        # Step 4: Chunk into 500-token segments
        logger.info(f"✂️  Chunking {len(html_chunks)} elements...")
        text_chunks = chunker.chunk_content(html_chunks)
        logger.info(f"📦 Created {len(text_chunks)} chunks")
        
        # Step 5: Check if URL already indexed (save Pinecone credits)
        if vector_store.url_exists(search_request.url):
            logger.info(f"♻️  URL already indexed, skipping re-indexing to save credits")
        else:
            # Index in vector database
            logger.info("💾 Indexing chunks...")
            vector_store.index_chunks(text_chunks, search_request.url)
        
        # Step 6: Semantic search
        logger.info("🔎 Performing semantic search...")
        results = vector_store.search(search_request.query, limit=10)
        
        logger.info(f"✅ Found {len(results)} results")
        
        # Step 7: Return response
        response = SearchResponse(
            results=[SearchResult(**r) for r in results],
            total_chunks=len(text_chunks),
            query=search_request.query
        )
        
        # Cache the response
        response_cache[cache_key] = response
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
