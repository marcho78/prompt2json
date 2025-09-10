from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from src.schemas.response_schemas import TemplateResponse, TemplateListResponse
from src.models.database import get_db, PromptTemplate
from src.api.dependencies_optional import get_current_user_optional
from src.models.database import User
import json
import os

router = APIRouter()


@router.get("/templates", response_model=TemplateListResponse)
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    complexity: Optional[str] = Query(None, description="Filter by complexity"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get list of available prompt templates (public endpoint with DB fallback)"""
    
    # Try to get templates from database first
    try:
        db = next(get_db())
        try:
            query = db.query(PromptTemplate).filter(PromptTemplate.is_active == True)
            
            if category:
                query = query.filter(PromptTemplate.category == category)
            if complexity:
                query = query.filter(PromptTemplate.complexity == complexity)
            
            templates = query.all()
            
            return TemplateListResponse(
                templates=[TemplateResponse.from_orm(template) for template in templates],
                total_count=len(templates)
            )
        finally:
            db.close()
    except Exception as db_error:
        # Fallback to static templates when DB is unavailable
        print(f"Warning: Database unavailable, using static templates: {db_error}")
        return _get_static_templates(category, complexity)


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get specific template by ID (public endpoint with DB fallback)"""
    
    try:
        db = next(get_db())
        try:
            template = db.query(PromptTemplate).filter(
                PromptTemplate.id == template_id,
                PromptTemplate.is_active == True
            ).first()
            
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            return TemplateResponse.from_orm(template)
        finally:
            db.close()
    except Exception as db_error:
        # Fallback to static template lookup
        static_templates = _get_static_templates()
        if template_id <= len(static_templates.templates):
            return static_templates.templates[template_id - 1]
        else:
            raise HTTPException(status_code=404, detail="Template not found")


def _get_static_templates(category: Optional[str] = None, complexity: Optional[str] = None) -> TemplateListResponse:
    """Fallback static templates when database is unavailable"""
    
    # Static template data - production ready examples
    static_templates_data = [
        {
            "id": 1,
            "name": "Customer Feedback Analysis",
            "description": "Template for analyzing customer feedback sentiment and extracting insights",
            "category": "analysis",
            "complexity": "simple",
            "template_data": {
                "task": "sentiment_analysis",
                "instructions": {
                    "primary_goal": "Analyze customer feedback to determine sentiment and extract key insights",
                    "steps": [
                        "Read the customer feedback carefully",
                        "Identify the overall sentiment (positive, negative, neutral)",
                        "Extract specific issues or praise mentioned",
                        "Categorize feedback by topic"
                    ]
                },
                "input_format": {"type": "string", "description": "Customer feedback text"},
                "output_format": {
                    "type": "object",
                    "properties": {
                        "sentiment": {"type": "string"},
                        "confidence": {"type": "number"},
                        "topics": {"type": "array"},
                        "summary": {"type": "string"}
                    }
                }
            },
            "created_at": "2025-01-10T22:00:00Z",
            "updated_at": "2025-01-10T22:00:00Z",
            "is_active": True
        },
        {
            "id": 2,
            "name": "Code Review Assistant",
            "description": "Template for systematic code review and improvement suggestions",
            "category": "development",
            "complexity": "moderate",
            "template_data": {
                "task": "code_review",
                "instructions": {
                    "primary_goal": "Review code for quality, security, and best practices",
                    "steps": [
                        "Analyze code structure and readability",
                        "Check for security vulnerabilities",
                        "Verify adherence to coding standards",
                        "Suggest improvements and optimizations"
                    ]
                },
                "input_format": {"type": "string", "description": "Code snippet to review"},
                "output_format": {
                    "type": "object",
                    "properties": {
                        "overall_quality": {"type": "string"},
                        "issues": {"type": "array"},
                        "suggestions": {"type": "array"},
                        "security_notes": {"type": "array"}
                    }
                }
            },
            "created_at": "2025-01-10T22:00:00Z",
            "updated_at": "2025-01-10T22:00:00Z",
            "is_active": True
        },
        {
            "id": 3,
            "name": "Content Summarization",
            "description": "Template for creating concise summaries of long-form content",
            "category": "writing",
            "complexity": "simple",
            "template_data": {
                "task": "summarization",
                "instructions": {
                    "primary_goal": "Create a concise, accurate summary of the provided content",
                    "steps": [
                        "Identify the main topics and key points",
                        "Extract the most important information",
                        "Create a structured summary",
                        "Ensure no critical information is lost"
                    ]
                },
                "input_format": {"type": "string", "description": "Long-form text to summarize"},
                "output_format": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "key_points": {"type": "array"},
                        "word_count": {"type": "number"}
                    }
                }
            },
            "created_at": "2025-01-10T22:00:00Z",
            "updated_at": "2025-01-10T22:00:00Z",
            "is_active": True
        }
    ]
    
    # Filter templates based on query parameters
    filtered_templates = static_templates_data
    if category:
        filtered_templates = [t for t in filtered_templates if t["category"] == category]
    if complexity:
        filtered_templates = [t for t in filtered_templates if t["complexity"] == complexity]
    
    # Convert to TemplateResponse objects
    template_responses = []
    for template_data in filtered_templates:
        template_responses.append(TemplateResponse(
            id=template_data["id"],
            name=template_data["name"],
            description=template_data["description"],
            category=template_data["category"],
            template_data=template_data["template_data"],
            complexity=template_data["complexity"],
            created_at=template_data["created_at"],
            updated_at=template_data["updated_at"],
            is_active=template_data["is_active"]
        ))
    
    return TemplateListResponse(
        templates=template_responses,
        total_count=len(template_responses)
    )
