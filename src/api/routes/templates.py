from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import json
from src.schemas.response_schemas import TemplateResponse, TemplateListResponse
from src.models.database import get_db, PromptTemplate
from src.api.dependencies_optional import get_current_user_optional
from src.models.database import User

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

            # If DB has no templates, fall back to static list
            if not templates:
                return _get_static_templates(category, complexity)

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
    """Fallback static templates when database is unavailable. Loads from templates/base_templates.json."""
    # Locate static file relative to project root
    base_file = Path(__file__).resolve().parents[3] / 'templates' / 'base_templates.json'
    try:
        with base_file.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Static templates file not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Static templates JSON parse error: {str(e)}")

    # Map to TemplateResponse list
    items: List[TemplateResponse] = []
    idx = 1
    for key, entry in data.items():
        item = TemplateResponse(
            id=idx,
            name=entry.get('name', key),
            description=entry.get('description', ''),
            category=entry.get('category', key),
            complexity=entry.get('complexity', 'moderate'),
            components=entry.get('components', []),
            created_at=datetime.utcnow()
        )
        items.append(item)
        idx += 1

    # Apply filters
    if category:
        items = [t for t in items if t.category == category]
    if complexity:
        items = [t for t in items if t.complexity == complexity]

    return TemplateListResponse(templates=items, total_count=len(items))
