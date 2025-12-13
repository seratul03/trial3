"""
Database models for the Teacher/Admin Panel
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, JSON, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
faq_tags = Table(
    'faq_tags',
    Base.metadata,
    Column('faq_id', Integer, ForeignKey('faqs.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

pdf_tags = Table(
    'pdf_tags',
    Base.metadata,
    Column('pdf_id', Integer, ForeignKey('pdf_documents.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

teacher_subjects = Table(
    'teacher_subjects',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete='CASCADE'))
)


class User(Base):
    """User model for teachers and admins"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='teacher')  # 'admin' or 'teacher'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subjects = relationship('Subject', secondary=teacher_subjects, back_populates='teachers')
    faqs = relationship('FAQ', back_populates='creator')
    pdfs = relationship('PDFDocument', back_populates='uploader')
    manual_responses = relationship('ManualResponse', back_populates='teacher')
    announcements = relationship('Announcement', back_populates='creator')


class Subject(Base):
    """Subject/Course model"""
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    semester = Column(Integer, nullable=True)
    department = Column(String(255), nullable=True)
    
    # Subject details as JSON
    course_outcomes = Column(JSON, default=list)  # List of strings
    prerequisites = Column(JSON, default=list)  # List of strings
    books = Column(JSON, default=list)  # List of {title, author, url}
    modules = Column(JSON, default=list)  # List of {number, title, description}
    internal_exam_info = Column(JSON, default=dict)  # {structure, marks}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    teachers = relationship('User', secondary=teacher_subjects, back_populates='subjects')
    faqs = relationship('FAQ', back_populates='subject')
    pdfs = relationship('PDFDocument', back_populates='subject')


class Tag(Base):
    """Tags for categorizing content"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    faqs = relationship('FAQ', secondary=faq_tags, back_populates='tags')
    pdfs = relationship('PDFDocument', secondary=pdf_tags, back_populates='tags')


class FAQ(Base):
    """Frequently Asked Questions"""
    __tablename__ = 'faqs'
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False, index=True)
    answer = Column(Text, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subject = relationship('Subject', back_populates='faqs')
    creator = relationship('User', back_populates='faqs')
    tags = relationship('Tag', secondary=faq_tags, back_populates='faqs')


class PDFDocument(Base):
    """Uploaded PDF documents"""
    __tablename__ = 'pdf_documents'
    
    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    uploader_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    extracted_text = Column(Text, nullable=True)  # Full-text extracted from PDF
    file_size = Column(Integer, nullable=True)  # Size in bytes
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    uploader = relationship('User', back_populates='pdfs')
    subject = relationship('Subject', back_populates='pdfs')
    tags = relationship('Tag', secondary=pdf_tags, back_populates='pdfs')


class StudentQuery(Base):
    """Student queries from chatbot"""
    __tablename__ = 'student_queries'
    
    id = Column(Integer, primary_key=True, index=True)
    student_identifier = Column(String(255), nullable=True)  # Anonymous or user ID
    question_text = Column(Text, nullable=False, index=True)
    bot_answer = Column(Text, nullable=True)
    attachments = Column(JSON, default=list)  # List of file paths
    status = Column(String(50), default='new', index=True)  # new, in_progress, resolved, ignored
    assigned_teacher_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assigned_teacher = relationship('User')
    subject = relationship('Subject')
    manual_responses = relationship('ManualResponse', back_populates='query', cascade='all, delete-orphan')
    feedback = relationship('Feedback', back_populates='query', uselist=False, cascade='all, delete-orphan')


class ManualResponse(Base):
    """Manual responses from teachers to student queries"""
    __tablename__ = 'manual_responses'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('student_queries.id', ondelete='CASCADE'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    response_text = Column(Text, nullable=False)
    added_to_kb_flag = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    query = relationship('StudentQuery', back_populates='manual_responses')
    teacher = relationship('User', back_populates='manual_responses')


class Announcement(Base):
    """Announcements and notices"""
    __tablename__ = 'announcements'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    attachments = Column(JSON, default=list)  # List of file paths
    visible_to_chatbot = Column(Boolean, default=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False, index=True)
    removed = Column(Boolean, default=False, index=True)
    
    # Relationships
    creator = relationship('User', back_populates='announcements')


class Feedback(Base):
    """Student feedback on bot answers"""
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('student_queries.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    helpful_bool = Column(Boolean, nullable=True)  # True=helpful, False=not helpful
    reviewed_bool = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    query = relationship('StudentQuery', back_populates='feedback')


class BotConfig(Base):
    """Bot configuration settings"""
    __tablename__ = 'bot_config'
    
    id = Column(Integer, primary_key=True)
    greeting_message = Column(Text, default="Hello! How can I help you today?")
    fallback_message = Column(Text, default="I'm sorry, I couldn't find an answer. A teacher will get back to you soon.")
    error_message = Column(Text, default="An error occurred. Please try again later.")
    tone = Column(String(50), default='academic')  # formal, friendly, academic
    contact_phone = Column(String(20), default='+1-234-567-8900')
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Audit trail for KB edits"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # 'faq', 'subject', etc.
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # 'create', 'update', 'delete'
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    edited_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    editor = relationship('User')


# Create indices for full-text search
from sqlalchemy import Index, text

# Full-text search indices (SQLite FTS5)
Index('idx_faq_question', FAQ.question)
Index('idx_faq_answer', FAQ.answer)
Index('idx_pdf_text', PDFDocument.extracted_text)
Index('idx_query_text', StudentQuery.question_text)
