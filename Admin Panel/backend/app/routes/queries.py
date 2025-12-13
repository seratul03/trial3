"""
Student Query Management routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime, date
from app.database import get_db
from app.models import StudentQuery, ManualResponse, User, FAQ, Tag, Feedback
from app.schemas import (
    StudentQueryCreate, QueryReplyCreate, QueryStatusUpdate,
    StandardResponse, FAQCreate
)
from app.auth import get_current_user
from app.utils import generate_unique_filename
import os
import json

router = APIRouter(prefix="/api/queries", tags=["Queries"])

ATTACHMENT_DIR = "uploads/attachments"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)


@router.get("", response_model=StandardResponse)
async def get_queries(
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    tag: Optional[str] = None,
    subject_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student queries with filters"""
    query = db.query(StudentQuery)
    
    # Status filter
    if status:
        query = query.filter(StudentQuery.status == status)
    
    # Date range filter
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(StudentQuery.created_at >= from_date)
        except:
            pass
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(StudentQuery.created_at <= to_date)
        except:
            pass
    
    # Subject filter
    if subject_id:
        query = query.filter(StudentQuery.subject_id == subject_id)
    
    # For teachers, only show queries assigned to them or unassigned
    if current_user.role == 'teacher':
        user_subject_ids = [s.id for s in current_user.subjects]
        query = query.filter(
            or_(
                StudentQuery.assigned_teacher_id == current_user.id,
                StudentQuery.subject_id.in_(user_subject_ids),
                StudentQuery.assigned_teacher_id.is_(None)
            )
        )
    
    # Pagination
    offset = (page - 1) * limit
    total = query.count()
    queries = query.order_by(StudentQuery.created_at.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "queries": [{
                "id": q.id,
                "student_identifier": q.student_identifier,
                "question_text": q.question_text,
                "bot_answer": q.bot_answer,
                "attachments": q.attachments or [],
                "status": q.status,
                "assigned_teacher_id": q.assigned_teacher_id,
                "subject_id": q.subject_id,
                "created_at": q.created_at.isoformat(),
                "resolved_at": q.resolved_at.isoformat() if q.resolved_at else None,
                "responses_count": len(q.manual_responses),
                "has_feedback": q.feedback is not None
            } for q in queries],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )


@router.get("/{query_id}", response_model=StandardResponse)
async def get_query_detail(
    query_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get query details with responses"""
    query = db.query(StudentQuery).filter(StudentQuery.id == query_id).first()
    
    if not query:
        return StandardResponse(success=False, error="Query not found", data=None)
    
    return StandardResponse(
        success=True,
        data={
            "id": query.id,
            "student_identifier": query.student_identifier,
            "question_text": query.question_text,
            "bot_answer": query.bot_answer,
            "attachments": query.attachments or [],
            "status": query.status,
            "assigned_teacher_id": query.assigned_teacher_id,
            "subject_id": query.subject_id,
            "created_at": query.created_at.isoformat(),
            "resolved_at": query.resolved_at.isoformat() if query.resolved_at else None,
            "responses": [{
                "id": r.id,
                "teacher_id": r.teacher_id,
                "response_text": r.response_text,
                "added_to_kb_flag": r.added_to_kb_flag,
                "created_at": r.created_at.isoformat()
            } for r in query.manual_responses],
            "feedback": {
                "comment": query.feedback.comment,
                "helpful_bool": query.feedback.helpful_bool,
                "reviewed_bool": query.feedback.reviewed_bool,
                "created_at": query.feedback.created_at.isoformat()
            } if query.feedback else None
        },
        error=None
    )


@router.post("", response_model=StandardResponse)
async def create_query(
    query_data: StudentQueryCreate,
    db: Session = Depends(get_db)
):
    """Create new student query (public endpoint for chatbot)"""
    new_query = StudentQuery(
        student_identifier=query_data.student_identifier,
        question_text=query_data.question_text,
        bot_answer=query_data.bot_answer,
        attachments=query_data.attachments,
        subject_id=query_data.subject_id,
        status='new'
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    return StandardResponse(
        success=True,
        data={
            "id": new_query.id,
            "status": new_query.status,
            "created_at": new_query.created_at.isoformat()
        },
        error=None
    )


@router.post("/{query_id}/reply", response_model=StandardResponse)
async def reply_to_query(
    query_id: int,
    reply_data: QueryReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Teacher replies to query and optionally adds to KB"""
    query = db.query(StudentQuery).filter(StudentQuery.id == query_id).first()
    
    if not query:
        return StandardResponse(success=False, error="Query not found", data=None)
    
    # Create manual response
    manual_response = ManualResponse(
        query_id=query_id,
        teacher_id=current_user.id,
        response_text=reply_data.response_text,
        added_to_kb_flag=reply_data.add_to_kb
    )
    
    db.add(manual_response)
    
    # If add_to_kb is true, create FAQ entry
    if reply_data.add_to_kb:
        faq_question = reply_data.faq_question or query.question_text
        
        new_faq = FAQ(
            question=faq_question,
            answer=reply_data.response_text,
            subject_id=query.subject_id,
            created_by=current_user.id
        )
        
        # Add tags if provided
        if reply_data.faq_tags:
            tags = db.query(Tag).filter(Tag.id.in_(reply_data.faq_tags)).all()
            new_faq.tags = tags
        
        db.add(new_faq)
    
    # Update query status
    if query.status == 'new':
        query.status = 'in_progress'
    
    db.commit()
    
    return StandardResponse(
        success=True,
        data={
            "message": "Reply added successfully",
            "added_to_kb": reply_data.add_to_kb
        },
        error=None
    )


@router.patch("/{query_id}", response_model=StandardResponse)
async def update_query_status(
    query_id: int,
    status_update: QueryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update query status"""
    query = db.query(StudentQuery).filter(StudentQuery.id == query_id).first()
    
    if not query:
        return StandardResponse(success=False, error="Query not found", data=None)
    
    query.status = status_update.status
    
    if status_update.assigned_teacher_id is not None:
        query.assigned_teacher_id = status_update.assigned_teacher_id
    
    if status_update.status == 'resolved':
        query.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": f"Query status updated to {status_update.status}"},
        error=None
    )


@router.get("/stats/summary", response_model=StandardResponse)
async def get_query_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get query statistics"""
    from datetime import date as date_class
    
    today = date_class.today()
    
    # Total queries today
    queries_today = db.query(StudentQuery).filter(
        func.date(StudentQuery.created_at) == today
    ).count()
    
    # Pending queries
    pending_queries = db.query(StudentQuery).filter(
        StudentQuery.status.in_(['new', 'in_progress'])
    ).count()
    
    # Total with feedback
    total_with_feedback = db.query(Feedback).count()
    helpful_feedback = db.query(Feedback).filter(Feedback.helpful_bool == True).count()
    
    accuracy = (helpful_feedback / total_with_feedback * 100) if total_with_feedback > 0 else 0
    
    return StandardResponse(
        success=True,
        data={
            "queries_today": queries_today,
            "pending_queries": pending_queries,
            "chatbot_accuracy": round(accuracy, 2)
        },
        error=None
    )
