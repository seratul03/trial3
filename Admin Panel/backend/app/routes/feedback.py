"""
Feedback and bot config routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Feedback, BotConfig, User, StudentQuery, FAQ, AuditLog
from app.schemas import FeedbackCreate, FeedbackUpdate, BotConfigUpdate, StandardResponse
from app.auth import get_current_user
import json

router = APIRouter(prefix="/api", tags=["Feedback & Config"])


# ============== Feedback Endpoints ==============
@router.get("/feedback", response_model=StandardResponse)
async def get_feedback(
    reviewed: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student feedback entries"""
    query = db.query(Feedback).join(StudentQuery)
    
    if reviewed is not None:
        query = query.filter(Feedback.reviewed_bool == reviewed)
    
    offset = (page - 1) * limit
    total = query.count()
    feedback_list = query.order_by(Feedback.created_at.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "feedback": [{
                "id": f.id,
                "query_id": f.query_id,
                "student_id": f.student_id,
                "comment": f.comment,
                "helpful_bool": f.helpful_bool,
                "reviewed_bool": f.reviewed_bool,
                "created_at": f.created_at.isoformat(),
                "query": {
                    "question_text": f.query.question_text,
                    "bot_answer": f.query.bot_answer
                }
            } for f in feedback_list],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )


@router.post("/feedback", response_model=StandardResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Create feedback (public endpoint for chatbot)"""
    # Check if feedback already exists for this query
    existing = db.query(Feedback).filter(Feedback.query_id == feedback_data.query_id).first()
    if existing:
        return StandardResponse(success=False, error="Feedback already exists for this query", data=None)
    
    new_feedback = Feedback(
        query_id=feedback_data.query_id,
        student_id=feedback_data.student_id,
        comment=feedback_data.comment,
        helpful_bool=feedback_data.helpful_bool
    )
    
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return StandardResponse(
        success=True,
        data={
            "id": new_feedback.id,
            "message": "Feedback submitted successfully"
        },
        error=None
    )


@router.patch("/feedback/{feedback_id}", response_model=StandardResponse)
async def update_feedback(
    feedback_id: int,
    feedback_update: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark feedback as reviewed"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        return StandardResponse(success=False, error="Feedback not found", data=None)
    
    feedback.reviewed_bool = feedback_update.reviewed_bool
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "Feedback updated successfully"},
        error=None
    )


@router.post("/feedback/{feedback_id}/fix-kb", response_model=StandardResponse)
async def fix_kb_from_feedback(
    feedback_id: int,
    faq_id: int,
    corrected_answer: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update FAQ based on feedback"""
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        return StandardResponse(success=False, error="Feedback not found", data=None)
    
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        return StandardResponse(success=False, error="FAQ not found", data=None)
    
    # Create audit log
    audit = AuditLog(
        entity_type='faq',
        entity_id=faq_id,
        action='update',
        old_value={"answer": faq.answer},
        new_value={"answer": corrected_answer},
        edited_by=current_user.id
    )
    
    # Update FAQ
    faq.answer = corrected_answer
    
    # Mark feedback as reviewed
    feedback.reviewed_bool = True
    
    db.add(audit)
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "FAQ updated successfully"},
        error=None
    )


# ============== Bot Config Endpoints ==============
@router.get("/bot-config", response_model=StandardResponse)
async def get_bot_config(
    db: Session = Depends(get_db)
):
    """Get bot configuration (public endpoint)"""
    config = db.query(BotConfig).first()
    
    if not config:
        # Create default config
        config = BotConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return StandardResponse(
        success=True,
        data={
            "greeting_message": config.greeting_message,
            "fallback_message": config.fallback_message,
            "error_message": config.error_message,
            "tone": config.tone,
            "contact_phone": config.contact_phone
        },
        error=None
    )


@router.put("/bot-config", response_model=StandardResponse)
async def update_bot_config(
    config_data: BotConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update bot configuration"""
    config = db.query(BotConfig).first()
    
    if not config:
        config = BotConfig()
        db.add(config)
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return StandardResponse(
        success=True,
        data={
            "message": "Bot configuration updated successfully",
            "config": {
                "greeting_message": config.greeting_message,
                "fallback_message": config.fallback_message,
                "error_message": config.error_message,
                "tone": config.tone,
                "contact_phone": config.contact_phone
            }
        },
        error=None
    )


# ============== Audit Log Endpoints ==============
@router.get("/audit-logs", response_model=StandardResponse)
async def get_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit trail of KB edits"""
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    
    offset = (page - 1) * limit
    total = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "logs": [{
                "id": log.id,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "action": log.action,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "edited_by": log.edited_by,
                "editor_name": log.editor.name if log.editor else None,
                "timestamp": log.timestamp.isoformat()
            } for log in logs],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )
