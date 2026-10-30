import fitz  # PyMuPDF
import re
import hashlib
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ExtractedPage:
    page_number: int
    text: str

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def calculate_hash(self, file_content: bytes) -> str:
        return hashlib.sha256(file_content).hexdigest()

    def extract_text(self, pdf_path: str) -> List[ExtractedPage]:
        pages = []
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                pages.append(ExtractedPage(page_number=page_num, text=text))
        return pages

    def normalize_text(self, text: str) -> str:
        # Remove excessive whitespace and normalize unicode
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, pages: List[ExtractedPage]) -> List[Tuple[int, int, str]]:
        """
        Splits pages into overlapping chunks.
        Returns a list of (page_number, chunk_index, content)
        """
        chunks = []
        for page in pages:
            normalized_text = self.normalize_text(page.text)
            if not normalized_text:
                continue

            start = 0
            chunk_idx = 0
            while start < len(normalized_text):
                end = start + self.chunk_size
                chunk_content = normalized_text[start:end]
                chunks.append((page.page_number, chunk_idx, chunk_content))

                start += (self.chunk_size - self.chunk_overlap)
                chunk_idx += 1
                if start >= len(normalized_text):
                    break
        return chunks
