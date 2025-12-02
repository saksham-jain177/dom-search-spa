import httpx
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import List, Dict
import re


class HTMLChunk:
    """Represents a chunk of HTML content with metadata"""
    def __init__(self, text: str, html: str, dom_path: str, position: int):
        self.text = text
        self.html = html
        self.dom_path = dom_path
        self.position = position


class HTMLParser:
    """Fetches and parses HTML content from URLs"""
    
    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def fetch_html(self, url: str) -> str:
        """Fetch HTML content from URL"""
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    
    def clean_html(self, html_content: str) -> BeautifulSoup:
        """Parse and clean HTML content"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        
        return soup
    
    def get_dom_path(self, element: Tag) -> str:
        """Generate DOM path for an element (e.g., 'html > body > div.main > p')"""
        path_parts = []
        current = element
        
        while current and current.name:
            # Build selector with class if available
            selector = current.name
            if current.get('class'):
                classes = ' '.join(current['class'])
                # Use first class for brevity
                selector += f".{current['class'][0]}"
            elif current.get('id'):
                selector += f"#{current['id']}"
            
            path_parts.insert(0, selector)
            current = current.parent
            
            # Limit depth
            if len(path_parts) >= 6:
                break
        
        return ' > '.join(path_parts)
    
    def extract_content_chunks(self, soup: BeautifulSoup) -> List[HTMLChunk]:
        """Extract text content with DOM paths and HTML snippets"""
        chunks = []
        position = 0
        
        # Find all content-bearing elements
        content_tags = soup.find_all(['p', 'div', 'article', 'section', 'li', 'td', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for element in content_tags:
            # Get text content (direct children only to avoid duplication)
            text = element.get_text(separator=' ', strip=True)
            
            # Skip if too short or empty
            if not text or len(text) < 20:
                continue
            
            # Get HTML snippet (limit to reasonable size)
            html_snippet = str(element)[:2000]  # Limit HTML size
            
            # Get DOM path
            dom_path = self.get_dom_path(element)
            
            chunks.append(HTMLChunk(
                text=text,
                html=html_snippet,
                dom_path=dom_path,
                position=position
            ))
            position += 1
        
        return chunks
    
    def close(self):
        """Close HTTP client"""
        self.client.close()
