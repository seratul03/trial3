"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserLogin, UserCreate, UserResponse, TokenResponse, StandardResponse
from app.auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_user, get_current_admin
)
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=StandardResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        return StandardResponse(
            success=False,
            error="Incorrect email or password",
            data=None
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    
    return StandardResponse(
        success=True,
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat()
            }
        },
        error=None
    )


@router.post("/logout", response_model=StandardResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should delete token)"""
    return StandardResponse(
        success=True,
        data={"message": "Logged out successfully"},
        error=None
    )


@router.get("/me", response_model=StandardResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return StandardResponse(
        success=True,
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat()
        },
        error=None
    )


@router.post("/users", response_model=StandardResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Create new user (admin only)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return StandardResponse(
            success=False,
            error="Email already registered",
            data=None
        )
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return StandardResponse(
        success=True,
        data={
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "created_at": new_user.created_at.isoformat()
        },
        error=None
    )


@router.get("/users", response_model=StandardResponse)
async def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """List all users (admin only)"""
    users = db.query(User).all()
    
    return StandardResponse(
        success=True,
        data=[{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat(),
            "subjects": [{"id": s.id, "name": s.name} for s in u.subjects]
        } for u in users],
        error=None
    )


@router.put("/users/{user_id}/subjects", response_model=StandardResponse)
async def assign_subjects_to_user(
    user_id: int,
    subject_ids: list[int],
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Assign subjects to a teacher (admin only)"""
    from app.models import Subject
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return StandardResponse(success=False, error="User not found", data=None)
    
    # Get subjects
    subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all()
    user.subjects = subjects
    
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": f"Assigned {len(subjects)} subjects to {user.name}"},
        error=None
    )
