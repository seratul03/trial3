"""
PDF text extraction utilities
"""
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from typing import Optional
import io


def extract_text_from_pdf(file_content: bytes, method: str = 'pypdf2') -> Optional[str]:
    """
    Extract text from PDF file content
    
    Args:
        file_content: PDF file as bytes
        method: 'pypdf2' or 'pdfminer'
    
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        if method == 'pdfminer':
            # Use pdfminer for better text extraction
            text = pdfminer_extract_text(io.BytesIO(file_content))
            return text.strip()
        else:
            # Use PyPDF2 (faster but less accurate)
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            text = '\n'.join(text_parts)
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal
    
    Args:
        filename: Original filename
    
    Returns:
        Safe filename
    """
    # Remove path components
    import os
    filename = os.path.basename(filename)
    
    # Remove or replace unsafe characters
    unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    return filename


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename with timestamp
    
    Args:
        original_filename: Original filename
    
    Returns:
        Unique filename
    """
    import uuid
    from datetime import datetime
    
    safe_name = sanitize_filename(original_filename)
    name_parts = safe_name.rsplit('.', 1)
    
    if len(name_parts) == 2:
        name, ext = name_parts
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{name}_{timestamp}_{unique_id}.{ext}"
    else:
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{safe_name}_{timestamp}_{unique_id}"
