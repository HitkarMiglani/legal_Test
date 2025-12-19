"""
Database models for LuminaryAI
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    """User role enumeration"""
    LAWYER = "lawyer"
    STUDENT = "student"
    PUBLIC = "public"

class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PUBLIC)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    """Document model"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    doc_id = Column(String(36), unique=True, nullable=False)  # UUID for document
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_hash = Column(String(64))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(String(20), default='pending')  # pending, processing, completed, failed
    
    # Cached processing results
    cached_text = Column(Text)  # Extracted and cleaned text
    cached_metadata = Column(Text)  # JSON string of metadata (char_count, word_count, etc.)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    analyses = relationship("Analysis", back_populates="document", cascade="all, delete-orphan")

class Query(Base):
    """User query model"""
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    context = Column(Text)  # JSON string of context used
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="queries")

class Analysis(Base):
    """Document analysis results"""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    analysis_type = Column(String(50), nullable=False)
    result = Column(Text)  # JSON string of analysis results
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="analyses")

class Memory(Base):
    """User memory/preferences"""
    __tablename__ = 'memories'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text)  # Encrypted value
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="memories")

class LegalCase(Base):
    """Legal case reference"""
    __tablename__ = 'legal_cases'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(String(100), unique=True)
    title = Column(String(500))
    court = Column(String(200))
    date = Column(DateTime)
    citation = Column(String(200))
    content = Column(Text)
    summary = Column(Text)
    keywords = Column(Text)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(database_url='sqlite:///luminary.db'):
    """Initialize the database"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()
