from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.config import settings

Base = declarative_base()

# Database engine and session
database_url = settings.get_database_url()
engine = create_engine(database_url, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prompts = relationship("GeneratedPrompt", back_populates="creator")


class PromptTemplate(Base):
    """Template model for storing reusable prompt templates"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, index=True)
    template_data = Column(JSON, nullable=False)
    complexity = Column(String, default="moderate")  # simple, moderate, complex
    components = Column(JSON)  # List of components used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class GeneratedPrompt(Base):
    """Model for storing generated prompts"""
    __tablename__ = "generated_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=False)  # Original user description
    target_llm = Column(String, nullable=False)  # claude, gpt-4, etc.
    complexity = Column(String, nullable=False)
    prompt_data = Column(JSON, nullable=False)  # The generated prompt
    prompt_metadata = Column(JSON)  # Token count, complexity score, etc.
    optimization_goals = Column(JSON)  # List of optimization goals
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="prompts")
    tests = relationship("PromptTest", back_populates="prompt")


class PromptTest(Base):
    """Model for storing prompt test results"""
    __tablename__ = "prompt_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("generated_prompts.id"), nullable=False)
    test_input = Column(Text, nullable=False)
    expected_output = Column(Text)
    actual_output = Column(Text)
    test_result = Column(String)  # pass, fail, error
    execution_time = Column(Float)
    token_usage = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prompt = relationship("GeneratedPrompt", back_populates="tests")


class OptimizationHistory(Base):
    """Model for tracking prompt optimizations"""
    __tablename__ = "optimization_history"
    
    id = Column(Integer, primary_key=True, index=True)
    original_prompt = Column(JSON, nullable=False)
    optimized_prompt = Column(JSON, nullable=False)
    optimization_criteria = Column(JSON)
    improvement_metrics = Column(JSON)  # Token reduction, clarity score, etc.
    target_model = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Create all database tables"""
    import os
    
    # Ensure database directory exists for SQLite
    if database_url.startswith('sqlite:///'):
        db_path = database_url.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")
    
    Base.metadata.create_all(bind=engine)
    print(f"Database tables created successfully at: {database_url}")
