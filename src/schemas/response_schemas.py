from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class UserResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()}, from_attributes=True)
    
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class PromptMetadata(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    estimated_tokens: int = Field(..., description="Estimated token count")
    complexity_score: float = Field(..., ge=0.0, le=1.0, description="Complexity score from 0 to 1")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")
    version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_models: List[str] = Field(default=[])


class GeneratePromptResponse(BaseModel):
    prompt: Dict[str, Any] = Field(..., description="The generated prompt structure")
    metadata: PromptMetadata


class OptimizePromptResponse(BaseModel):
    original_prompt: Dict[str, Any]
    optimized_prompt: Dict[str, Any]
    improvements: List[str]
    metrics: Dict[str, Any] = Field(default={})


class ConvertPromptResponse(BaseModel):
    converted_prompt: Dict[str, Any]
    source_format: str
    target_format: str
    conversion_notes: List[str] = Field(default=[])


class TestPromptResponse(BaseModel):
    test_id: str
    result: str  # pass, fail, error
    execution_time: float
    actual_output: str
    expected_output: Optional[str] = None
    token_usage: Optional[int] = None
    errors: List[str] = Field(default=[])


class MergePromptsResponse(BaseModel):
    merged_prompt: Dict[str, Any]
    merge_strategy: str
    components_count: int
    metadata: Dict[str, Any] = Field(default={})


class QualityIssue(BaseModel):
    type: str
    severity: str  # low, medium, high, critical
    description: str
    suggestion: str


class AnalyzePromptResponse(BaseModel):
    quality_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[QualityIssue]
    improvements: List[str]
    metrics: Dict[str, Any] = Field(default={})


class TemplateResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()}, from_attributes=True)
    
    id: int
    name: str
    description: str
    category: str
    complexity: str
    components: List[str] = Field(default=[])
    created_at: datetime


class TemplateListResponse(BaseModel):
    templates: List[TemplateResponse]
    total_count: int


class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    error: str
    detail: str
    code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
