import os
import re
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional, Union
import pymupdf  # PyMuPDF
from backend.models import DocumentMetadata

class DocumentParser:
    """High-performance document parser with exact page grounding and text block extraction."""

    @staticmethod
    def parse_pdf(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parses a PDF document into page-by-page structured contents.
        Extracts plain text, structured blocks, and header metadata.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        doc = pymupdf.open(str(path))
        pages_data = []
        total_chars = 0

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1  # 1-indexed for citation consistency
            text = page.get_text("text")
            total_chars += len(text)

            # Extract structured blocks with bounding information
            blocks = page.get_text("blocks")
            cleaned_blocks = []
            for b in blocks:
                # b is (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5 and b[4].strip():
                    cleaned_blocks.append({
                        "bbox": (b[0], b[1], b[2], b[3]),
                        "text": b[4].strip(),
                        "block_no": b[5] if len(b) > 5 else 0
                    })

            # Detect potential section headers (heuristic: short lines with uppercase or title case at top)
            section_title = None
            if cleaned_blocks:
                first_block = cleaned_blocks[0]["text"]
                first_line = first_block.split("\n")[0].strip()
                if len(first_line) < 80 and not first_line.isdigit():
                    section_title = first_line

            # Extract structured tables with bounding information and context header
            tables_data = []
            should_check_tables = False
            if len(doc) <= 25:
                should_check_tables = bool(re.search(r'\d', text))
            else:
                num_count = len(re.findall(r'\b\d+(?:,\d+)?(?:\.\d+)?\b', text))
                has_keywords = bool(re.search(r'particulars|consolidated|statement|quarter|year ended|crore|million|billion|in %|metrics|segment|growth', text, re.I))
                should_check_tables = num_count >= 8 and has_keywords

            if should_check_tables:
                try:
                    found_tables = page.find_tables()
                    if found_tables and found_tables.tables:
                        for t in found_tables.tables:
                            extracted = t.extract()
                            if extracted and len(extracted) >= 2:
                                bbox = getattr(t, "bbox", None)
                                header_clip = ""
                                if bbox:
                                    try:
                                        header_clip = page.get_text("text", clip=(0, max(0, bbox[1] - 80), page.rect.width, bbox[1])).strip()
                                    except Exception:
                                        pass
                                tables_data.append({
                                    "grid": extracted,
                                    "bbox": bbox,
                                    "header_clip": header_clip
                                })
                except Exception:
                    pass

            pages_data.append({
                "page_number": page_num,
                "text": text,
                "blocks": cleaned_blocks,
                "tables": tables_data,
                "section_title": section_title,
                "char_count": len(text)
            })

        metadata = DocumentMetadata(
            filename=path.name,
            filepath=str(path.resolve()),
            page_count=len(doc),
            file_size_bytes=path.stat().st_size,
            facts_count=0
        )

        doc.close()

        return {
            "metadata": metadata,
            "pages": pages_data,
            "total_chars": total_chars
        }

    @staticmethod
    def extract_context_window(text: str, target_quote: str, window_chars: int = 250) -> str:
        """
        Extracts surrounding context window around a quote for verification.
        """
        if not target_quote or not text:
            return ""

        pos = text.lower().find(target_quote.lower().strip())
        if pos == -1:
            # Try finding first 30 chars
            sub = target_quote.strip()[:30].lower()
            pos = text.lower().find(sub)

        if pos == -1:
            return text[:min(len(text), window_chars * 2)]

        start = max(0, pos - window_chars)
        end = min(len(text), pos + len(target_quote) + window_chars)
        snippet = text[start:end].strip().replace("\n", " ")
        return f"...{snippet}..." if start > 0 or end < len(text) else snippet

    @staticmethod
    def stream_pdf_chunks(file_path: Union[str, Path], chunk_size_pages: int = 5) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Yields batches of pages for streaming large PDFs without memory bloat.
        """
        path = Path(file_path)
        doc = pymupdf.open(str(path))
        batch = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_data = {
                "document_name": path.name,
                "page_number": page_idx + 1,
                "text": page.get_text("text")
            }
            batch.append(page_data)

            if len(batch) >= chunk_size_pages:
                yield batch
                batch = []

        if batch:
            yield batch

        doc.close()
