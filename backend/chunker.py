import re
import logging

logger = logging.getLogger("chunker")

class SmartChunker:
    def __init__(self, target_chunk_size=500, overlap_size=50):
        self.target_chunk_size = target_chunk_size
        self.overlap_size = overlap_size

    def chunk_document(self, parsed_doc):
        """Main entry point. Dynamically select chunking strategy based on source type."""
        source_type = parsed_doc.get("source_type")
        source_name = parsed_doc.get("source")
        raw_chunks = parsed_doc.get("chunks", [])
        
        logger.info(f"Chunking document: {source_name} (Type: {source_type}) with {len(raw_chunks)} raw items")
        
        final_chunks = []
        
        for idx, chunk in enumerate(raw_chunks):
            text = chunk.get("text", "")
            chunk_type = chunk.get("type", "paragraph")
            metadata = chunk.get("metadata", {}).copy()
            metadata["source"] = source_name
            metadata["source_type"] = source_type
            metadata["raw_chunk_idx"] = idx
            
            if not text.strip():
                continue
                
            if source_type in ('pdf', 'txt', 'audio'):
                # Sentence-based chunking
                split_chunks = self._chunk_by_sentence(text, chunk_type, metadata)
            elif source_type in ('docx', 'markdown', 'html', 'web'):
                # Paragraph-based chunking
                split_chunks = self._chunk_by_paragraph(text, chunk_type, metadata)
            elif source_type in ('pptx', 'email'):
                # Section-based chunking
                split_chunks = self._chunk_by_section(text, chunk_type, metadata)
            elif source_type in ('json', 'xml'):
                # Key-value chunking
                split_chunks = self._chunk_by_key_value(text, chunk_type, metadata)
            elif source_type in ('csv', 'sqlite'):
                # Row-based chunking
                split_chunks = self._chunk_by_row(text, chunk_type, metadata)
            elif source_type == 'image':
                # OCR-line chunking
                split_chunks = self._chunk_by_ocr_line(text, chunk_type, metadata)
            elif source_type == 'video':
                # Timeline-based chunking (already structured by timeline in parser)
                split_chunks = self._chunk_by_timeline(text, chunk_type, metadata)
            else:
                # Default fallback
                split_chunks = self._chunk_by_paragraph(text, chunk_type, metadata)
                
            final_chunks.extend(split_chunks)
            
        # Give a unique chunk ID to all final chunks
        for i, chunk in enumerate(final_chunks):
            chunk["chunk_id"] = f"{source_name}_chunk_{i}"
            
        logger.info(f"Generated {len(final_chunks)} final chunks for {source_name}")
        return final_chunks

    def _chunk_by_sentence(self, text, chunk_type, metadata):
        """Split text into sentences and group them to match the target size."""
        # Simple sentence tokenizer regex
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_len = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_len = len(sentence)
            if current_len + sentence_len > self.target_chunk_size and current_chunk:
                chunks.append({
                    "text": " ".join(current_chunk),
                    "type": chunk_type,
                    "metadata": metadata
                })
                # Maintain overlap (last sentence or two)
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], sentence]
                    current_len = len(current_chunk[0]) + 1 + sentence_len
                else:
                    current_chunk = [sentence]
                    current_len = sentence_len
            else:
                current_chunk.append(sentence)
                current_len += (1 if current_len > 0 else 0) + sentence_len
                
        if current_chunk:
            chunks.append({
                "text": " ".join(current_chunk),
                "type": chunk_type,
                "metadata": metadata
            })
            
        return chunks

    def _chunk_by_paragraph(self, text, chunk_type, metadata):
        """Split text by paragraphs and group them."""
        paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]
        chunks = []
        current_chunk = []
        current_len = 0
        
        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len > self.target_chunk_size and current_chunk:
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "type": chunk_type,
                    "metadata": metadata
                })
                current_chunk = [para]
                current_len = para_len
            else:
                current_chunk.append(para)
                current_len += (1 if current_len > 0 else 0) + para_len
                
        if current_chunk:
            chunks.append({
                "text": "\n".join(current_chunk),
                "type": chunk_type,
                "metadata": metadata
            })
            
        return chunks

    def _chunk_by_section(self, text, chunk_type, metadata):
        """Split by logical sections (e.g. Slide content or EML headers/body)."""
        # Slides and Emails have pre-defined chunks, we just cap size if too large.
        if len(text) <= self.target_chunk_size * 1.5:
            return [{
                "text": text,
                "type": chunk_type,
                "metadata": metadata
            }]
        else:
            return self._chunk_by_paragraph(text, chunk_type, metadata)

    def _chunk_by_key_value(self, text, chunk_type, metadata):
        """Split structured key-values (JSON/XML) into readable groupings."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        chunks = []
        current_chunk = []
        
        # Group every 15 entries/lines together
        group_size = 15
        for idx, line in enumerate(lines):
            current_chunk.append(line)
            if len(current_chunk) >= group_size:
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "type": "paragraph",
                    "metadata": metadata
                })
                current_chunk = []
                
        if current_chunk:
            chunks.append({
                "text": "\n".join(current_chunk),
                "type": "paragraph",
                "metadata": metadata
            })
            
        return chunks

    def _chunk_by_row(self, text, chunk_type, metadata):
        """Group rows for CSV and database dumps, keeping schema header."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return []
            
        header = lines[0]
        data_rows = lines[1:] if len(lines) > 1 else []
        
        chunks = []
        current_chunk = []
        
        # Group every 10 rows
        group_size = 10
        for row in data_rows:
            current_chunk.append(row)
            if len(current_chunk) >= group_size:
                chunks.append({
                    "text": f"Columns: {header}\n" + "\n".join(current_chunk),
                    "type": "table",
                    "metadata": metadata
                })
                current_chunk = []
                
        if current_chunk or not data_rows:
            rows_text = "\n".join(current_chunk) if current_chunk else "[Empty Data Rows]"
            chunks.append({
                "text": f"Columns: {header}\n" + rows_text,
                "type": "table",
                "metadata": metadata
            })
            
        return chunks

    def _chunk_by_ocr_line(self, text, chunk_type, metadata):
        """Parse image OCR text by splitting on multiple lines."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        chunks = []
        current_chunk = []
        current_len = 0
        
        for line in lines:
            line_len = len(line)
            if current_len + line_len > self.target_chunk_size and current_chunk:
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "type": "ocr",
                    "metadata": metadata
                })
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += (1 if current_len > 0 else 0) + line_len
                
        if current_chunk:
            chunks.append({
                "text": "\n".join(current_chunk),
                "type": "ocr",
                "metadata": metadata
            })
            
        return chunks

    def _chunk_by_timeline(self, text, chunk_type, metadata):
        """Video timeline segment cap."""
        # Visual slide description or audio subtitle is kept inside its window
        return [{
            "text": text,
            "type": chunk_type,
            "metadata": metadata
        }]
