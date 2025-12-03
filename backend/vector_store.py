from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tqdm import tqdm
import os
import time

class VectorStore:
    """Pinecone vector database wrapper"""
    
    def __init__(self):
        # Initialize Pinecone
        # Get API key from environment variable
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            print("⚠️ PINECONE_API_KEY not found in environment variables")
            # Fallback for demo if user hasn't set it yet
            # In production, always use env vars
            pass
            
        self.pc = Pinecone(api_key=api_key)
        self.index_name = "semantic-search-demo"
        self.index = None
        
        # Lazy load model
        self._model = None
        self.dim = 384  # all-MiniLM-L6-v2 embedding dimension

    @property
    def model(self):
        if self._model is None:
            print("⏳ Loading SentenceTransformer model...")
            # Force CPU usage and optimize for low memory
            self._model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
            self._model.max_seq_length = 256
            print("✅ Model loaded")
        return self._model
    
    def _ensure_index(self):
        """Lazy load index and create if doesn't exist"""
        if self.index is not None:
            return

        try:
            existing_indexes = [i.name for i in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dim,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    time.sleep(1)
            
            self.index = self.pc.Index(self.index_name)
            print("✅ Pinecone index initialized")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            raise
    
    def index_chunks(self, chunks: List[Dict], source_url: str):
        """
        Index chunks into Pinecone
        """
        self._ensure_index()
            
        # Generate embeddings
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False, batch_size=8)
        
        # Prepare vectors for upsert
        vectors = []
        for i, chunk in enumerate(chunks):
            # Create a unique ID for the vector
            vector_id = f"{source_url}_{i}"
            
            # Metadata must be simple types
            metadata = {
                "content": chunk['content'],
                "html": chunk['html'],
                "dom_path": chunk['dom_path'],
                "url": source_url,
                "position": chunk['position']
            }
            
            vectors.append({
                "id": vector_id,
                "values": embeddings[i].tolist(),
                "metadata": metadata
            })
            
        # Upsert in batches of 100
        batch_size = 100
        total_batches = (len(vectors) + batch_size - 1) // batch_size
        
        print(f"📤 Uploading {len(chunks)} chunks in {total_batches} batches...")
        for i in tqdm(range(0, len(vectors), batch_size), desc="Indexing", unit="batch"):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            
        print(f"✅ Indexed {len(chunks)} chunks to Pinecone")
    
    def search(self, query: str, limit: int = 10, url_filter: str = None) -> List[Dict]:
        """
        Perform semantic search with optional URL filtering
        """
        self._ensure_index()
            
        # Generate query embedding
        query_embedding = self.model.encode(query, show_progress_bar=False, batch_size=8)
        
        # Prepare filter
        filter_dict = {}
        if url_filter:
            filter_dict["url"] = {"$eq": url_filter}
        
        # Search
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=limit,
            include_metadata=True,
            filter=filter_dict if url_filter else None
        )
        
        # Format results
        formatted_results = []
        for match in results['matches']:
            # Cosine similarity - clamp to 1.0 to handle floating point precision
            score = min(match['score'], 1.0)
            
            formatted_results.append({
                "score": round(score, 4),
                "percentage": min(int(score * 100), 100),
                "dom_path": match['metadata'].get("dom_path", ""),
                "chunk_text": match['metadata'].get("content", ""),
                "chunk_html": match['metadata'].get("html", ""),
                "url": match['metadata'].get("url", "")
            })
        
        return formatted_results
    
    def url_exists(self, url: str) -> bool:
        """Check if URL has already been indexed"""
        if self.index is None:
            self.index = self.pc.Index(self.index_name)
        
        try:
            # Query for any vector with this URL
            results = self.index.query(
                vector=[0.0] * self.dim,  # Dummy vector
                filter={"url": {"$eq": url}},
                top_k=1,
                include_metadata=False
            )
            return len(results.get('matches', [])) > 0
        except:
            return False
    
    def clear_url_data(self, url: str):
        """Delete all vectors for a specific URL"""
        if self.index is None:
            self.index = self.pc.Index(self.index_name)
            
        try:
            # Delete by metadata filter
            self.index.delete(
                filter={"url": {"$eq": url}}
            )
        except Exception as e:
            print(f"Error clearing URL data: {e}")
    
    def close(self):
        pass
