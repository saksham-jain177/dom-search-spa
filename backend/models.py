from pydantic import BaseModel, HttpUrl, Field
from typing import List


class SearchRequest(BaseModel):
    """Request model for search endpoint"""
    url: str = Field(..., description="Website URL to scrape and search")
    query: str = Field(..., min_length=1, description="Search query")


class SearchResult(BaseModel):
    """Individual search result"""
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    percentage: int = Field(..., ge=0, le=100, description="Match percentage (0-100)")
    dom_path: str = Field(..., description="DOM path of the chunk")
    chunk_text: str = Field(..., description="Text preview of the chunk")
    chunk_html: str = Field(..., description="Raw HTML snippet")


class SearchResponse(BaseModel):
    """Response model containing search results"""
    results: List[SearchResult] = Field(default_factory=list, max_length=10)
    total_chunks: int = Field(..., description="Total chunks processed")
    query: str = Field(..., description="Original query")
