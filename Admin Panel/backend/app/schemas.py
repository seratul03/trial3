"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== Auth Schemas ==============
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = 'teacher'


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse


# ============== Subject Schemas ==============
class SubjectCreate(BaseModel):
    code: str
    name: str
    semester: Optional[int] = None
    department: Optional[str] = None
    course_outcomes: List[str] = []
    prerequisites: List[str] = []
    books: List[Dict[str, str]] = []
    modules: List[Dict[str, Any]] = []
    internal_exam_info: Dict[str, Any] = {}


class SubjectUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    semester: Optional[int] = None
    department: Optional[str] = None
    course_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    books: Optional[List[Dict[str, str]]] = None
    modules: Optional[List[Dict[str, Any]]] = None
    internal_exam_info: Optional[Dict[str, Any]] = None


class SubjectResponse(BaseModel):
    id: int
    code: str
    name: str
    semester: Optional[int]
    department: Optional[str]
    course_outcomes: List[str]
    prerequisites: List[str]
    books: List[Dict[str, str]]
    modules: List[Dict[str, Any]]
    internal_exam_info: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============== Tag Schemas ==============
class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== FAQ Schemas ==============
class FAQCreate(BaseModel):
    question: str
    answer: str
    subject_id: Optional[int] = None
    tag_ids: List[int] = []


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    subject_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class FAQResponse(BaseModel):
    id: int
    question: str
    answer: str
    subject_id: Optional[int]
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


# ============== PDF Schemas ==============
class PDFUploadResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    subject_id: Optional[int]
    file_size: Optional[int]
    uploaded_at: datetime
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class PDFDetailResponse(PDFUploadResponse):
    extracted_text: Optional[str]
    uploader_id: Optional[int]


# ============== Query Schemas ==============
class StudentQueryCreate(BaseModel):
    student_identifier: Optional[str] = None
    question_text: str
    bot_answer: Optional[str] = None
    attachments: List[str] = []
    subject_id: Optional[int] = None


class QueryReplyCreate(BaseModel):
    response_text: str
    add_to_kb: bool = False
    faq_question: Optional[str] = None
    faq_tags: List[int] = []


class QueryStatusUpdate(BaseModel):
    status: str  # new, in_progress, resolved, ignored
    assigned_teacher_id: Optional[int] = None


class StudentQueryResponse(BaseModel):
    id: int
    student_identifier: Optional[str]
    question_text: str
    bot_answer: Optional[str]
    attachments: List[str]
    status: str
    assigned_teacher_id: Optional[int]
    subject_id: Optional[int]
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============== Announcement Schemas ==============
class AnnouncementCreate(BaseModel):
    title: str
    body: str
    attachments: List[str] = []
    visible_to_chatbot: bool = True
    scheduled_at: Optional[datetime] = None
    removed: bool = False


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    attachments: Optional[List[str]] = None
    visible_to_chatbot: Optional[bool] = None
    scheduled_at: Optional[datetime] = None
    removed: Optional[bool] = None


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    body: str
    attachments: List[str]
    visible_to_chatbot: bool
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    created_by: Optional[int]
    created_at: datetime
    is_active: bool
    removed: bool
    
    class Config:
        from_attributes = True


# ============== Feedback Schemas ==============
class FeedbackCreate(BaseModel):
    query_id: int
    student_id: Optional[str] = None
    comment: Optional[str] = None
    helpful_bool: Optional[bool] = None


class FeedbackUpdate(BaseModel):
    reviewed_bool: bool


class FeedbackResponse(BaseModel):
    id: int
    query_id: int
    student_id: Optional[str]
    comment: Optional[str]
    helpful_bool: Optional[bool]
    reviewed_bool: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Bot Config Schemas ==============
class BotConfigUpdate(BaseModel):
    greeting_message: Optional[str] = None
    fallback_message: Optional[str] = None
    error_message: Optional[str] = None
    tone: Optional[str] = None
    contact_phone: Optional[str] = None


class BotConfigResponse(BaseModel):
    greeting_message: str
    fallback_message: str
    error_message: str
    tone: str
    contact_phone: str
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============== Analytics Schemas ==============
class DashboardStats(BaseModel):
    total_queries_today: int
    pending_queries: int
    total_faqs: int
    total_pdfs: int
    chatbot_accuracy: float


class TopicCount(BaseModel):
    name: str
    count: int


class AnalyticsResponse(BaseModel):
    top_subjects: List[TopicCount]
    top_tags: List[TopicCount]
    confusing_questions: List[Dict[str, Any]]
    subjects_needing_data: List[Dict[str, Any]]


# ============== Standard Response ==============
class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
