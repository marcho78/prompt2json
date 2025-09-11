from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class OutputFormat(BaseModel):
    type: str = Field(..., description="Output data type")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Object properties if type is object")
    required: List[str] = Field(default=[], description="Required fields")


class InputFormat(BaseModel):
    type: str = Field(..., description="Input data type")
    description: str = Field(..., description="Description of expected input")
    constraints: List[str] = Field(default=[], description="Input constraints")


class Instructions(BaseModel):
    primary_goal: str = Field(..., description="Main objective of the prompt")
    steps: List[str] = Field(default=[], description="Step-by-step instructions")
    context: Optional[str] = Field(default=None, description="Additional context")


class Example(BaseModel):
    input: Any = Field(..., description="Example input")
    output: Any = Field(..., description="Expected output")
    explanation: Optional[str] = Field(default=None, description="Explanation of the example")


class PromptMetadata(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_models: List[str] = Field(default=[])
    estimated_tokens: int = Field(default=0)


class ReasoningFramework(BaseModel):
    type: str = Field(..., description="Type of reasoning framework")  # step_by_step, tree_of_thought, self_consistency
    depth: int = Field(default=1, description="Depth of reasoning")


class ChainOfThought(BaseModel):
    enabled: bool = Field(default=False)
    steps: List[str] = Field(default=[])


class FewShotLearning(BaseModel):
    examples: List[Example] = Field(default=[])
    example_selection: str = Field(default="diverse", description="Strategy for example selection")  # random, diverse, similar


class OutputValidation(BaseModel):
    json_schema: Optional[Dict[str, Any]] = Field(default=None)
    regex_patterns: List[str] = Field(default=[])
    custom_validators: List[str] = Field(default=[])


class PromptComponent(BaseModel):
    chain_of_thought: Optional[ChainOfThought] = Field(default=None)
    few_shot_learning: Optional[FewShotLearning] = Field(default=None)
    output_validation: Optional[OutputValidation] = Field(default=None)
    reasoning_framework: Optional[ReasoningFramework] = Field(default=None)


class PromptStructure(BaseModel):
    """
    Complete structure for an AI prompt based on the app-req.json specification
    """
    task: str = Field(..., description="Task identifier")
    system_message: Optional[str] = Field(default=None, description="System message for the LLM")
    instructions: Instructions = Field(..., description="Detailed instructions")
    input_format: InputFormat = Field(..., description="Expected input format")
    output_format: OutputFormat = Field(..., description="Expected output format")
    examples: List[Example] = Field(default=[], description="Example inputs and outputs")
    constraints: List[str] = Field(default=[], description="Additional constraints")
    edge_cases: List[str] = Field(default=[], description="Edge cases to consider")
    components: Optional[PromptComponent] = Field(default=None, description="Advanced prompt components")
    metadata: PromptMetadata = Field(default_factory=PromptMetadata, description="Metadata about the prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "data_extraction",
                "system_message": "You are an expert data extraction specialist.",
                "instructions": {
                    "primary_goal": "Extract structured data from unstructured text",
                    "steps": [
                        "Analyze the input text carefully",
                        "Identify relevant data points",
                        "Structure the data according to the output format"
                    ],
                    "context": "Focus on accuracy and completeness"
                },
                "input_format": {
                    "type": "string",
                    "description": "Unstructured text containing data to extract",
                    "constraints": ["Non-empty text", "UTF-8 encoding"]
                },
                "output_format": {
                    "type": "object",
                    "properties": {
                        "entities": {"type": "array"},
                        "relationships": {"type": "array"}
                    },
                    "required": ["entities"]
                },
                "examples": [
                    {
                        "input": "John Doe works at ABC Corp as a Software Engineer",
                        "output": {
                            "entities": [
                                {"type": "person", "name": "John Doe"},
                                {"type": "company", "name": "ABC Corp"},
                                {"type": "position", "title": "Software Engineer"}
                            ]
                        },
                        "explanation": "Basic entity extraction example"
                    }
                ]
            }
        }
