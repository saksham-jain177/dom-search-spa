from transformers import AutoTokenizer
from typing import List, Dict
from html_parser import HTMLChunk


class TextChunker:
    """Chunks text into 500-token segments using bert-base-uncased tokenizer"""
    
    def __init__(self, max_tokens: int = 500, overlap_tokens: int = 50):
        self._tokenizer = None
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    @property
    def tokenizer(self):
        if self._tokenizer is None:
            self._tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        return self._tokenizer
    
    def chunk_content(self, html_chunks: List[HTMLChunk]) -> List[Dict]:
        """
        Split HTML chunks into token-based chunks with metadata
        
        Args:
            html_chunks: List of HTMLChunk objects from parser
            
        Returns:
            List of dictionaries with chunked content and metadata
        """
        result_chunks = []
        
        for html_chunk in html_chunks:
            text = html_chunk.text
            
            # Tokenize the text
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
            
            # If the text is already within limit, keep as single chunk
            if len(tokens) <= self.max_tokens:
                result_chunks.append({
                    'content': text,
                    'html': html_chunk.html,
                    'dom_path': html_chunk.dom_path,
                    'position': html_chunk.position,
                    'token_count': len(tokens),
                    'chunk_index': 0
                })
            else:
                # Split into overlapping chunks
                chunk_index = 0
                start = 0
                
                while start < len(tokens):
                    end = min(start + self.max_tokens, len(tokens))
                    chunk_tokens = tokens[start:end]
                    
                    # Decode back to text
                    chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                    
                    result_chunks.append({
                        'content': chunk_text,
                        'html': html_chunk.html,  # Keep original HTML
                        'dom_path': html_chunk.dom_path,
                        'position': html_chunk.position,
                        'token_count': len(chunk_tokens),
                        'chunk_index': chunk_index
                    })
                    
                    # Move forward with overlap
                    start = end - self.overlap_tokens if end < len(tokens) else end
                    chunk_index += 1
        
        return result_chunks
    
    def get_token_count(self, text: str) -> int:
        """Get token count for a text string"""
        return len(self.tokenizer.encode(text, add_special_tokens=False))
