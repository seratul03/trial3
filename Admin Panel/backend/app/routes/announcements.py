"""
Announcement routes with scheduling
"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
import os
import uuid
from pathlib import Path
from app.database import get_db
from app.models import Announcement, User
from app.schemas import AnnouncementCreate, AnnouncementUpdate, StandardResponse
from app.auth import get_current_user
from app.scheduler import schedule_announcement

router = APIRouter(prefix="/api/announcements", tags=["Announcements"])

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "uploads" / "attachments"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/active", response_model=StandardResponse)
async def get_active_announcements(
    db: Session = Depends(get_db)
):
    """Get active announcements (public endpoint for chatbot)"""
    now = datetime.utcnow()
    
    announcements = db.query(Announcement).filter(
        and_(
            Announcement.is_active == True,
            Announcement.visible_to_chatbot == True,
            Announcement.published_at <= now
        )
    ).order_by(Announcement.published_at.desc()).limit(10).all()
    
    return StandardResponse(
        success=True,
        data=[{
            "id": a.id,
            "title": a.title,
            "body": a.body,
            "attachments": a.attachments or [],
            "published_at": a.published_at.isoformat()
        } for a in announcements],
        error=None
    )


@router.get("", response_model=StandardResponse)
async def get_announcements(
    page: int = 1,
    limit: int = 50,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all announcements (admin/teacher view)"""
    query = db.query(Announcement)
    
    if not include_inactive:
        query = query.filter(Announcement.is_active == True)
    
    offset = (page - 1) * limit
    total = query.count()
    announcements = query.order_by(Announcement.created_at.desc()).offset(offset).limit(limit).all()
    
    return StandardResponse(
        success=True,
        data={
            "announcements": [{
                "id": a.id,
                "title": a.title,
                "body": a.body,
                "attachments": a.attachments or [],
                "visible_to_chatbot": a.visible_to_chatbot,
                "scheduled_at": a.scheduled_at.isoformat() if a.scheduled_at else None,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "created_by": a.created_by,
                "created_at": a.created_at.isoformat(),
                "is_active": a.is_active,
                "removed": a.removed
            } for a in announcements],
            "total": total,
            "page": page,
            "limit": limit
        },
        error=None
    )


@router.get("/{announcement_id}", response_model=StandardResponse)
async def get_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get announcement by ID"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        return StandardResponse(success=False, error="Announcement not found", data=None)
    
    return StandardResponse(
        success=True,
        data={
            "id": announcement.id,
            "title": announcement.title,
            "body": announcement.body,
            "attachments": announcement.attachments or [],
            "visible_to_chatbot": announcement.visible_to_chatbot,
            "scheduled_at": announcement.scheduled_at.isoformat() if announcement.scheduled_at else None,
            "published_at": announcement.published_at.isoformat() if announcement.published_at else None,
            "created_by": announcement.created_by,
            "created_at": announcement.created_at.isoformat(),
            "is_active": announcement.is_active,
            "removed": announcement.removed
        },
        error=None
    )


@router.post("", response_model=StandardResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new announcement"""

    new_announcement = Announcement(
        title=announcement_data.title,
        body=announcement_data.body,
        attachments=announcement_data.attachments,
        visible_to_chatbot=announcement_data.visible_to_chatbot,
        scheduled_at=announcement_data.scheduled_at,
        created_by=current_user.id
    )

    # If no schedule, publish immediately
    if announcement_data.scheduled_at is None:
        new_announcement.published_at = datetime.utcnow()
        new_announcement.is_active = True

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)

    # Schedule for future publication (after ID is available)
    if announcement_data.scheduled_at is not None:
        new_announcement.is_active = False
        schedule_announcement(db, new_announcement.id, announcement_data.scheduled_at)
        db.commit()
        db.refresh(new_announcement)

    return StandardResponse(
        success=True,
        data={
            "id": new_announcement.id,
            "title": new_announcement.title,
            "scheduled_at": new_announcement.scheduled_at.isoformat() if new_announcement.scheduled_at else None,
            "is_active": new_announcement.is_active,
            "message": "Announcement scheduled" if new_announcement.scheduled_at else "Announcement published"
        },
        error=None
    )


@router.put("/{announcement_id}", response_model=StandardResponse)
async def update_announcement(
    announcement_id: int,
    announcement_data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update announcement"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        return StandardResponse(success=False, error="Announcement not found", data=None)
    
    # Update fields
    update_data = announcement_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)
    
    db.commit()
    db.refresh(announcement)
    
    return StandardResponse(
        success=True,
        data={
            "id": announcement.id,
            "title": announcement.title,
            "message": "Announcement updated successfully"
        },
        error=None
    )


@router.delete("/{announcement_id}", response_model=StandardResponse)
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete announcement (soft delete - mark as inactive)"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        return StandardResponse(success=False, error="Announcement not found", data=None)
    
    # Mark as removed (permanent)
    announcement.removed = True
    db.commit()
    return StandardResponse(
        success=True,
        data={"message": "Announcement marked as removed"},
        error=None
    )


@router.post("/{announcement_id}/publish", response_model=StandardResponse)
async def publish_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually publish a scheduled announcement"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        return StandardResponse(success=False, error="Announcement not found", data=None)
    
    announcement.published_at = datetime.utcnow()
    announcement.is_active = True
    
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "Announcement published successfully"},
        error=None
    )


@router.post("/upload", response_model=StandardResponse)
async def upload_attachments(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload attachment files for announcements"""
    try:
        file_paths = []
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.txt'}
        max_file_size = 10 * 1024 * 1024  # 10MB
        
        for file in files:
            # Validate file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return StandardResponse(
                    success=False,
                    error=f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}",
                    data=None
                )
            
            # Read file content
            content = await file.read()
            
            # Validate file size
            if len(content) > max_file_size:
                return StandardResponse(
                    success=False,
                    error=f"File {file.filename} exceeds 10MB limit",
                    data=None
                )
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Store relative path
            relative_path = f"/uploads/attachments/{unique_filename}"
            file_paths.append(relative_path)
        
        return StandardResponse(
            success=True,
            data={
                "message": f"Uploaded {len(file_paths)} file(s) successfully",
                "file_paths": file_paths
            },
            error=None
        )
        
    except Exception as e:
        return StandardResponse(
            success=False,
            error=f"Error uploading files: {str(e)}",
            data=None
        )
