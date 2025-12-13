"""
Knowledge Base routes (FAQs, PDFs, Tags, Subjects)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from app.database import get_db
from app.models import FAQ, PDFDocument, Tag, Subject, User
from app.schemas import (
    FAQCreate, FAQUpdate, FAQResponse, TagCreate, TagResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse, StandardResponse,
    PDFUploadResponse, PDFDetailResponse
)
from app.auth import get_current_user, check_user_permission
from app.utils import extract_text_from_pdf, generate_unique_filename
import os
import shutil
import json
import bleach

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])

UPLOAD_DIR = "uploads/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============== FAQ Endpoints ==============
@router.get("/faqs", response_model=StandardResponse)
async def get_faqs(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    subject_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get FAQs with optional filters"""
    query = db.query(FAQ)
    
    # Search filter
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                FAQ.question.like(search_term),
                FAQ.answer.like(search_term)
            )
        )
    
    # Tag filter
    if tag:
        query = query.join(FAQ.tags).filter(Tag.name == tag)
    
    # Subject filter
    if subject_id:
        query = query.filter(FAQ.subject_id == subject_id)
    
    # Pagination
    offset = (page - 1) * limit
    total = query.count()
    faqs = query.order_by(FAQ.created_at.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "faqs": [{
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "subject_id": faq.subject_id,
                "created_by": faq.created_by,
                "created_at": faq.created_at.isoformat(),
                "updated_at": faq.updated_at.isoformat() if faq.updated_at else None,
                "tags": [{"id": t.id, "name": t.name} for t in faq.tags]
            } for faq in faqs],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )


@router.post("/faqs", response_model=StandardResponse)
async def create_faq(
    faq_data: FAQCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new FAQ"""
    # Check permission
    if not check_user_permission(current_user, faq_data.subject_id, db):
        return StandardResponse(success=False, error="Insufficient permissions", data=None)
    
    # Sanitize HTML in answer
    clean_answer = bleach.clean(
        faq_data.answer,
        tags=['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'code', 'pre'],
        attributes={'a': ['href', 'title']}
    )
    
    new_faq = FAQ(
        question=faq_data.question,
        answer=clean_answer,
        subject_id=faq_data.subject_id,
        created_by=current_user.id
    )
    
    # Add tags
    if faq_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(faq_data.tag_ids)).all()
        new_faq.tags = tags
    
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    
    return StandardResponse(
        success=True,
        data={
            "id": new_faq.id,
            "question": new_faq.question,
            "answer": new_faq.answer,
            "subject_id": new_faq.subject_id,
            "created_by": new_faq.created_by,
            "created_at": new_faq.created_at.isoformat(),
            "tags": [{"id": t.id, "name": t.name} for t in new_faq.tags]
        },
        error=None
    )


@router.put("/faqs/{faq_id}", response_model=StandardResponse)
async def update_faq(
    faq_id: int,
    faq_data: FAQUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        return StandardResponse(success=False, error="FAQ not found", data=None)
    
    # Check permission
    if not check_user_permission(current_user, faq.subject_id, db):
        return StandardResponse(success=False, error="Insufficient permissions", data=None)
    
    # Update fields
    if faq_data.question is not None:
        faq.question = faq_data.question
    if faq_data.answer is not None:
        faq.answer = bleach.clean(
            faq_data.answer,
            tags=['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a', 'code', 'pre'],
            attributes={'a': ['href', 'title']}
        )
    if faq_data.subject_id is not None:
        faq.subject_id = faq_data.subject_id
    if faq_data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(faq_data.tag_ids)).all()
        faq.tags = tags
    
    db.commit()
    db.refresh(faq)
    
    return StandardResponse(
        success=True,
        data={
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer,
            "subject_id": faq.subject_id,
            "tags": [{"id": t.id, "name": t.name} for t in faq.tags]
        },
        error=None
    )


@router.delete("/faqs/{faq_id}", response_model=StandardResponse)
async def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        return StandardResponse(success=False, error="FAQ not found", data=None)
    
    # Check permission
    if not check_user_permission(current_user, faq.subject_id, db):
        return StandardResponse(success=False, error="Insufficient permissions", data=None)
    
    db.delete(faq)
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "FAQ deleted successfully"},
        error=None
    )


# ============== PDF Endpoints ==============
@router.post("/pdfs", response_model=StandardResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    subject_id: Optional[int] = Form(None),
    tag_ids: str = Form("[]"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload PDF and extract text"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        return StandardResponse(success=False, error="Only PDF files are allowed", data=None)
    
    # Validate file size (max 20MB)
    content = await file.read()
    file_size = len(content)
    if file_size > 20 * 1024 * 1024:
        return StandardResponse(success=False, error="File size exceeds 20MB limit", data=None)
    
    # Check permission
    if not check_user_permission(current_user, subject_id, db):
        return StandardResponse(success=False, error="Insufficient permissions", data=None)
    
    # Generate unique filename and save
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Extract text from PDF
    extracted_text = extract_text_from_pdf(content, method='pdfminer')
    
    # Parse tag IDs
    try:
        tag_id_list = json.loads(tag_ids)
    except:
        tag_id_list = []
    
    # Create PDF document record
    pdf_doc = PDFDocument(
        original_filename=file.filename,
        stored_filename=unique_filename,
        uploader_id=current_user.id,
        subject_id=subject_id,
        extracted_text=extracted_text,
        file_size=file_size
    )
    
    # Add tags
    if tag_id_list:
        tags = db.query(Tag).filter(Tag.id.in_(tag_id_list)).all()
        pdf_doc.tags = tags
    
    db.add(pdf_doc)
    db.commit()
    db.refresh(pdf_doc)
    
    return StandardResponse(
        success=True,
        data={
            "id": pdf_doc.id,
            "original_filename": pdf_doc.original_filename,
            "stored_filename": pdf_doc.stored_filename,
            "subject_id": pdf_doc.subject_id,
            "file_size": pdf_doc.file_size,
            "uploaded_at": pdf_doc.uploaded_at.isoformat(),
            "tags": [{"id": t.id, "name": t.name} for t in pdf_doc.tags],
            "text_extracted": extracted_text is not None
        },
        error=None
    )


@router.get("/pdfs", response_model=StandardResponse)
async def get_pdfs(
    subject_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of uploaded PDFs"""
    query = db.query(PDFDocument)
    
    if subject_id:
        query = query.filter(PDFDocument.subject_id == subject_id)
    
    offset = (page - 1) * limit
    total = query.count()
    pdfs = query.order_by(PDFDocument.uploaded_at.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "pdfs": [{
                "id": pdf.id,
                "original_filename": pdf.original_filename,
                "subject_id": pdf.subject_id,
                "file_size": pdf.file_size,
                "uploaded_at": pdf.uploaded_at.isoformat(),
                "tags": [{"id": t.id, "name": t.name} for t in pdf.tags]
            } for pdf in pdfs],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )


@router.get("/pdfs/{pdf_id}", response_model=StandardResponse)
async def get_pdf_detail(
    pdf_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get PDF details including extracted text"""
    pdf = db.query(PDFDocument).filter(PDFDocument.id == pdf_id).first()
    if not pdf:
        return StandardResponse(success=False, error="PDF not found", data=None)
    
    return StandardResponse(
        success=True,
        data={
            "id": pdf.id,
            "original_filename": pdf.original_filename,
            "stored_filename": pdf.stored_filename,
            "subject_id": pdf.subject_id,
            "uploader_id": pdf.uploader_id,
            "file_size": pdf.file_size,
            "uploaded_at": pdf.uploaded_at.isoformat(),
            "extracted_text": pdf.extracted_text,
            "tags": [{"id": t.id, "name": t.name} for t in pdf.tags]
        },
        error=None
    )


# ============== Tag Endpoints ==============
@router.get("/tags", response_model=StandardResponse)
async def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tags"""
    tags = db.query(Tag).order_by(Tag.name).all()
    
    return StandardResponse(
        success=True,
        data=[{"id": t.id, "name": t.name} for t in tags],
        error=None
    )


@router.post("/tags", response_model=StandardResponse)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new tag"""
    # Check if tag exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        return StandardResponse(success=False, error="Tag already exists", data=None)
    
    new_tag = Tag(name=tag_data.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return StandardResponse(
        success=True,
        data={"id": new_tag.id, "name": new_tag.name},
        error=None
    )


@router.delete("/tags/{tag_id}", response_model=StandardResponse)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return StandardResponse(success=False, error="Tag not found", data=None)
    
    db.delete(tag)
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "Tag deleted successfully"},
        error=None
    )


# ============== Search Endpoint ==============
@router.get("/search", response_model=StandardResponse)
async def search_knowledge_base(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Full-text search across FAQs and PDFs"""
    search_term = f"%{q}%"
    
    # Search FAQs
    faqs = db.query(FAQ).filter(
        or_(
            FAQ.question.like(search_term),
            FAQ.answer.like(search_term)
        )
    ).limit(20).all()
    
    # Search PDFs
    pdfs = db.query(PDFDocument).filter(
        or_(
            PDFDocument.original_filename.like(search_term),
            PDFDocument.extracted_text.like(search_term)
        )
    ).limit(20).all()
    
    return StandardResponse(
        success=True,
        data={
            "faqs": [{
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer[:200] + "..." if len(faq.answer) > 200 else faq.answer,
                "subject_id": faq.subject_id,
                "tags": [{"id": t.id, "name": t.name} for t in faq.tags]
            } for faq in faqs],
            "pdfs": [{
                "id": pdf.id,
                "original_filename": pdf.original_filename,
                "subject_id": pdf.subject_id,
                "snippet": pdf.extracted_text[:200] + "..." if pdf.extracted_text and len(pdf.extracted_text) > 200 else pdf.extracted_text
            } for pdf in pdfs]
        },
        error=None
    )
