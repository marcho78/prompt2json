from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class TargetLLM(str, Enum):
    CLAUDE = "claude"
    GPT_4 = "gpt-4"
    GEMINI = "gemini"
    LLAMA = "llama"


class Complexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class OptimizationGoal(str, Enum):
    CLARITY = "clarity"
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"
    TOKEN_REDUCTION = "token_reduction"


class MergeStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


# Authentication schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Prompt generation schemas
class GeneratePromptRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Natural language description of the prompt")
    target_llm: TargetLLM = Field(default=TargetLLM.CLAUDE)
    complexity: Complexity = Field(default=Complexity.MODERATE)
    include_examples: bool = Field(default=True)
    optimization_goals: List[OptimizationGoal] = Field(default=[OptimizationGoal.CLARITY])


class OptimizePromptRequest(BaseModel):
    prompt: Dict[str, Any] = Field(..., description="The prompt to optimize")
    target_model: str = Field(..., description="Target model for optimization")
    optimization_criteria: List[str] = Field(..., description="Optimization criteria")


class ConvertPromptRequest(BaseModel):
    prompt: Dict[str, Any] = Field(..., description="The prompt to convert")
    source_format: str = Field(..., description="Source LLM format")
    target_format: str = Field(..., description="Target LLM format")


class TestPromptRequest(BaseModel):
    prompt: Dict[str, Any] = Field(..., description="The prompt to test")
    test_input: str = Field(..., description="Sample input for testing")
    target_model: str = Field(..., description="Target model to test with")


class MergePromptsRequest(BaseModel):
    prompts: List[Dict[str, Any]] = Field(..., min_items=2, description="Prompts to merge")
    merge_strategy: MergeStrategy = Field(default=MergeStrategy.SEQUENTIAL)


class AnalyzePromptRequest(BaseModel):
    prompt: Dict[str, Any] = Field(..., description="The prompt to analyze")


# Template schemas
class TemplateQuery(BaseModel):
    category: Optional[str] = None
    complexity: Optional[str] = None
