
"""
Analytics and logs routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional
from datetime import datetime, timedelta, date
import requests
import os
from app.database import get_db
from app.models import (
    StudentQuery, FAQ, PDFDocument, Tag, Subject,
    Feedback, User, faq_tags
)
from app.schemas import StandardResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Student chatbot URL (main app)
STUDENT_CHATBOT_URL = os.environ.get("STUDENT_CHATBOT_URL", "http://localhost:8000")


@router.get("/dashboard", response_model=StandardResponse)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard overview statistics - combines local DB and student chatbot data"""
    today = date.today()
    
    # Try to fetch real-time data from student chatbot
    external_stats = None
    try:
        response = requests.get(f"{STUDENT_CHATBOT_URL}/api/admin/stats", timeout=5)
        if response.ok:
            result = response.json()
            if result.get('success'):
                external_stats = result.get('data')
    except Exception as e:
        print(f"[WARNING] Could not fetch external stats: {e}")
    
    # Use external stats if available, otherwise use local DB
    if external_stats:
        queries_today = external_stats.get('queries_today', 0)
        pending_queries = external_stats.get('pending_queries', 0)
        total_faqs = external_stats.get('total_faqs', 0)
        accuracy = external_stats.get('chatbot_accuracy', 0)
        total_pdfs = external_stats.get('total_pdfs', 0)
    else:
        # Fallback to local database queries
        queries_today = db.query(StudentQuery).filter(
            func.date(StudentQuery.created_at) == today
        ).count()
        
        pending_queries = db.query(StudentQuery).filter(
            StudentQuery.status.in_(['new', 'in_progress'])
        ).count()
        
        total_faqs = db.query(FAQ).count()
        total_pdfs = db.query(PDFDocument).count()
        
        # Chatbot accuracy
        total_feedback = db.query(Feedback).filter(Feedback.helpful_bool.isnot(None)).count()
        helpful_count = db.query(Feedback).filter(Feedback.helpful_bool == True).count()
        accuracy = (helpful_count / total_feedback * 100) if total_feedback > 0 else 0
    
    # Most asked topics (top 5 tags) - always from local DB
    tag_counts = db.query(
        Tag.name, func.count(faq_tags.c.faq_id).label('count')
    ).join(faq_tags).group_by(Tag.id).order_by(desc('count')).limit(5).all()
    
    # Recent activity (last 10 queries) - from local DB
    recent_queries = db.query(StudentQuery).order_by(
        StudentQuery.created_at.desc()
    ).limit(10).all()
    
    return StandardResponse(
        success=True,
        data={
            "stats": {
                "queries_today": queries_today,
                "pending_queries": pending_queries,
                "total_faqs": total_faqs,
                "total_pdfs": total_pdfs,
                "chatbot_accuracy": round(accuracy, 2),
                "data_source": "real-time" if external_stats else "local"
            },
            "top_tags": [{"name": tag, "count": count} for tag, count in tag_counts],
            "recent_activity": [{
                "id": q.id,
                "type": "query",
                "text": q.question_text[:100],
                "status": q.status,
                "created_at": q.created_at.isoformat()
            } for q in recent_queries]
        },
        error=None
    )


@router.get("/top-subjects", response_model=StandardResponse)
async def get_top_subjects(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most queried subjects"""
    subject_counts = db.query(
        Subject.name, func.count(StudentQuery.id).label('count')
    ).join(StudentQuery, Subject.id == StudentQuery.subject_id, isouter=True)\
    .group_by(Subject.id).order_by(desc('count')).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data=[{"name": name or "Unassigned", "count": count} for name, count in subject_counts],
        error=None
    )


@router.get("/confusing-questions", response_model=StandardResponse)
async def get_confusing_questions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get questions with lowest helpful percentage"""
    # Get queries with feedback
    query_feedback = db.query(
        StudentQuery.id,
        StudentQuery.question_text,
        StudentQuery.bot_answer,
        Feedback.helpful_bool
    ).join(Feedback).filter(Feedback.helpful_bool == False).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data=[{
            "query_id": qf[0],
            "question": qf[1],
            "bot_answer": qf[2][:100] + "..." if qf[2] and len(qf[2]) > 100 else qf[2],
            "helpful": qf[3]
        } for qf in query_feedback],
        error=None
    )


@router.get("/subjects-needing-data", response_model=StandardResponse)
async def get_subjects_needing_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subjects with high queries but low KB coverage"""
    # Count queries per subject
    query_counts = db.query(
        Subject.id, Subject.name, func.count(StudentQuery.id).label('query_count')
    ).join(StudentQuery, Subject.id == StudentQuery.subject_id, isouter=True)\
    .group_by(Subject.id).all()
    
    # Count FAQs per subject
    faq_counts = db.query(
        Subject.id, func.count(FAQ.id).label('faq_count')
    ).join(FAQ, Subject.id == FAQ.subject_id, isouter=True)\
    .group_by(Subject.id).all()
    
    faq_dict = {subject_id: count for subject_id, count in faq_counts}
    
    # Calculate ratio
    results = []
    for subject_id, subject_name, query_count in query_counts:
        faq_count = faq_dict.get(subject_id, 0)
        ratio = query_count / (faq_count + 1)  # +1 to avoid division by zero
        
        if query_count > 5:  # Only subjects with at least 5 queries
            results.append({
                "subject_id": subject_id,
                "subject_name": subject_name,
                "query_count": query_count,
                "faq_count": faq_count,
                "coverage_ratio": round(ratio, 2)
            })
    
    # Sort by coverage ratio (higher means needs more data)
    results.sort(key=lambda x: x['coverage_ratio'], reverse=True)
    
    return StandardResponse(
        success=True,
        data=results[:10],
        error=None
    )


@router.get("/improvement-trend", response_model=StandardResponse)
async def get_improvement_trend(
    period: str = 'week',  # 'week' or 'month'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chatbot improvement trend over time"""
    days = 7 if period == 'week' else 30
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get feedback data grouped by date
    feedback_by_date = db.query(
        func.date(Feedback.created_at).label('date'),
        func.count(Feedback.id).label('total'),
        func.sum(func.cast(Feedback.helpful_bool, func.Integer)).label('helpful')
    ).filter(
        Feedback.created_at >= start_date,
        Feedback.helpful_bool.isnot(None)
    ).group_by(func.date(Feedback.created_at)).all()
    
    trend_data = []
    for date_val, total, helpful in feedback_by_date:
        accuracy = (helpful / total * 100) if total > 0 else 0
        trend_data.append({
            "date": str(date_val),
            "total_feedback": total,
            "helpful_count": helpful or 0,
            "accuracy": round(accuracy, 2)
        })
    
    return StandardResponse(
        success=True,
        data=trend_data,
        error=None
    )


@router.get("/logs", response_model=StandardResponse)
async def get_query_logs(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    tag: Optional[str] = None,
    department: Optional[str] = None,
    semester: Optional[int] = None,
    unresolved_only: bool = False,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed query logs with filters"""
    query = db.query(StudentQuery)
    
    # Date filters
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
    
    # Subject filters
    if department or semester:
        query = query.join(Subject, StudentQuery.subject_id == Subject.id, isouter=True)
        if department:
            query = query.filter(Subject.department == department)
        if semester:
            query = query.filter(Subject.semester == semester)
    
    # Unresolved filter
    if unresolved_only:
        query = query.filter(StudentQuery.status.in_(['new', 'in_progress']))
    
    # Pagination
    offset = (page - 1) * limit
    total = query.count()
    logs = query.order_by(StudentQuery.created_at.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "logs": [{
                "id": log.id,
                "student_identifier": log.student_identifier,
                "question_text": log.question_text,
                "bot_answer": log.bot_answer,
                "status": log.status,
                "subject_id": log.subject_id,
                "created_at": log.created_at.isoformat(),
                "resolved_at": log.resolved_at.isoformat() if log.resolved_at else None,
                "has_feedback": log.feedback is not None,
                "helpful": log.feedback.helpful_bool if log.feedback else None
            } for log in logs],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )


@router.get("/export-logs", response_model=StandardResponse)
async def export_logs_csv(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export query logs as CSV data"""
    query = db.query(StudentQuery)
    
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
    
    logs = query.order_by(StudentQuery.created_at.desc()).all()
    
    # Generate CSV data
    csv_rows = []
    csv_rows.append("ID,Student ID,Question,Bot Answer,Status,Created At,Resolved At")
    
    for log in logs:
        row = [
            str(log.id),
            log.student_identifier or "Anonymous",
            f'"{log.question_text.replace('"', '""')}"',
            f'"{(log.bot_answer or "").replace('"', '""')}"',
            log.status,
            log.created_at.isoformat(),
            log.resolved_at.isoformat() if log.resolved_at else ""
        ]
        csv_rows.append(",".join(row))
    
    csv_content = "\n".join(csv_rows)
    
    return StandardResponse(
        success=True,
        data={"csv": csv_content, "row_count": len(logs)},
        error=None
    )
