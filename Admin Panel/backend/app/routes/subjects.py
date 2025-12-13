"""
Subject management routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Subject, User
from app.schemas import SubjectCreate, SubjectUpdate, StandardResponse
from app.auth import get_current_user, get_current_admin
import json

router = APIRouter(prefix="/api/subjects", tags=["Subjects"])


@router.get("", response_model=StandardResponse)
async def get_subjects(
    department: Optional[str] = None,
    semester: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all subjects with optional filters"""
    query = db.query(Subject)
    
    if department:
        query = query.filter(Subject.department == department)
    if semester:
        query = query.filter(Subject.semester == semester)
    
    subjects = query.order_by(Subject.code).all()
    
    return StandardResponse(
        success=True,
        data=[{
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "semester": s.semester,
            "department": s.department,
            "course_outcomes": s.course_outcomes or [],
            "prerequisites": s.prerequisites or [],
            "books": s.books or [],
            "modules": s.modules or [],
            "internal_exam_info": s.internal_exam_info or {},
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        } for s in subjects],
        error=None
    )


@router.get("/{subject_id}", response_model=StandardResponse)
async def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subject by ID"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        return StandardResponse(success=False, error="Subject not found", data=None)
    
    return StandardResponse(
        success=True,
        data={
            "id": subject.id,
            "code": subject.code,
            "name": subject.name,
            "semester": subject.semester,
            "department": subject.department,
            "course_outcomes": subject.course_outcomes or [],
            "prerequisites": subject.prerequisites or [],
            "books": subject.books or [],
            "modules": subject.modules or [],
            "internal_exam_info": subject.internal_exam_info or {},
            "created_at": subject.created_at.isoformat(),
            "updated_at": subject.updated_at.isoformat() if subject.updated_at else None
        },
        error=None
    )


@router.post("", response_model=StandardResponse)
async def create_subject(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Create new subject (admin only)"""
    # Check if code already exists
    existing = db.query(Subject).filter(Subject.code == subject_data.code).first()
    if existing:
        return StandardResponse(success=False, error="Subject code already exists", data=None)
    
    new_subject = Subject(
        code=subject_data.code,
        name=subject_data.name,
        semester=subject_data.semester,
        department=subject_data.department,
        course_outcomes=subject_data.course_outcomes,
        prerequisites=subject_data.prerequisites,
        books=subject_data.books,
        modules=subject_data.modules,
        internal_exam_info=subject_data.internal_exam_info
    )
    
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return StandardResponse(
        success=True,
        data={
            "id": new_subject.id,
            "code": new_subject.code,
            "name": new_subject.name,
            "semester": new_subject.semester,
            "department": new_subject.department
        },
        error=None
    )


@router.put("/{subject_id}", response_model=StandardResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update subject"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        return StandardResponse(success=False, error="Subject not found", data=None)
    
    # Check permission (admin or assigned teacher)
    if current_user.role != 'admin':
        user_subject_ids = [s.id for s in current_user.subjects]
        if subject_id not in user_subject_ids:
            return StandardResponse(success=False, error="Insufficient permissions", data=None)
    
    # Update fields
    update_data = subject_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    
    db.commit()
    db.refresh(subject)
    
    return StandardResponse(
        success=True,
        data={
            "id": subject.id,
            "code": subject.code,
            "name": subject.name,
            "semester": subject.semester,
            "department": subject.department,
            "course_outcomes": subject.course_outcomes or [],
            "prerequisites": subject.prerequisites or [],
            "books": subject.books or [],
            "modules": subject.modules or [],
            "internal_exam_info": subject.internal_exam_info or {}
        },
        error=None
    )


@router.delete("/{subject_id}", response_model=StandardResponse)
async def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Delete subject (admin only)"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        return StandardResponse(success=False, error="Subject not found", data=None)
    
    db.delete(subject)
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "Subject deleted successfully"},
        error=None
    )


@router.get("/{subject_id}/export", response_model=StandardResponse)
async def export_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export subject data as JSON"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        return StandardResponse(success=False, error="Subject not found", data=None)
    
    export_data = {
        "code": subject.code,
        "name": subject.name,
        "semester": subject.semester,
        "department": subject.department,
        "course_outcomes": subject.course_outcomes or [],
        "prerequisites": subject.prerequisites or [],
        "books": subject.books or [],
        "modules": subject.modules or [],
        "internal_exam_info": subject.internal_exam_info or {}
    }
    
    return StandardResponse(
        success=True,
        data=export_data,
        error=None
    )


@router.post("/{subject_id}/import", response_model=StandardResponse)
async def import_subject(
    subject_id: int,
    import_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import subject data from JSON"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    
    if not subject:
        return StandardResponse(success=False, error="Subject not found", data=None)
    
    # Check permission
    if current_user.role != 'admin':
        user_subject_ids = [s.id for s in current_user.subjects]
        if subject_id not in user_subject_ids:
            return StandardResponse(success=False, error="Insufficient permissions", data=None)
    
    # Update fields from import data
    allowed_fields = ['course_outcomes', 'prerequisites', 'books', 'modules', 'internal_exam_info']
    for field in allowed_fields:
        if field in import_data:
            setattr(subject, field, import_data[field])
    
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "Subject data imported successfully"},
        error=None
    )
