from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.schemas.response_schemas import TemplateResponse, TemplateListResponse
from src.models.database import get_db, PromptTemplate
from src.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/templates", response_model=TemplateListResponse)
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    complexity: Optional[str] = Query(None, description="Filter by complexity"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of available prompt templates"""
    
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


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get specific template by ID"""
    
    template = db.query(PromptTemplate).filter(
        PromptTemplate.id == template_id,
        PromptTemplate.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse.from_orm(template)
