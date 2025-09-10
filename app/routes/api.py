from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

router = APIRouter()


class JSONPromptRequest(BaseModel):
    data: Dict[str, Any]
    template: Optional[str] = None
    format_type: Optional[str] = "simple"


class JSONPromptResponse(BaseModel):
    prompt: str
    metadata: Dict[str, Any]


@router.post("/json-to-prompt", response_model=JSONPromptResponse)
async def convert_json_to_prompt(request: JSONPromptRequest):
    """
    Convert JSON data to a formatted prompt
    """
    try:
        # Basic JSON to prompt conversion
        if request.format_type == "simple":
            prompt = _format_simple_prompt(request.data)
        elif request.format_type == "structured":
            prompt = _format_structured_prompt(request.data)
        else:
            prompt = _format_custom_prompt(request.data, request.template)
        
        return JSONPromptResponse(
            prompt=prompt,
            metadata={
                "format_type": request.format_type,
                "data_size": len(str(request.data)),
                "has_template": request.template is not None
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing JSON: {str(e)}")


def _format_simple_prompt(data: Dict[str, Any]) -> str:
    """Format JSON data as a simple prompt"""
    lines = []
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            lines.append(f"{key}: {json.dumps(value, indent=2)}")
        else:
            lines.append(f"{key}: {value}")
    return "\\n".join(lines)


def _format_structured_prompt(data: Dict[str, Any]) -> str:
    """Format JSON data as a structured prompt with sections"""
    prompt_parts = ["=== Data Structure ==="]
    
    def format_nested_data(obj, indent=0):
        lines = []
        prefix = "  " * indent
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.extend(format_nested_data(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                lines.append(f"{prefix}[{i}]:")
                lines.extend(format_nested_data(item, indent + 1))
        else:
            lines.append(f"{prefix}{obj}")
        
        return lines
    
    prompt_parts.extend(format_nested_data(data))
    return "\\n".join(prompt_parts)


def _format_custom_prompt(data: Dict[str, Any], template: Optional[str]) -> str:
    """Format JSON data using a custom template"""
    if not template:
        return _format_simple_prompt(data)
    
    # Simple template substitution - can be enhanced
    prompt = template
    for key, value in data.items():
        placeholder = f"{{{key}}}"
        if placeholder in prompt:
            prompt = prompt.replace(placeholder, str(value))
    
    return prompt


@router.get("/templates")
async def get_available_templates():
    """Get list of available prompt templates"""
    return {
        "templates": [
            {
                "name": "simple",
                "description": "Simple key-value format"
            },
            {
                "name": "structured",
                "description": "Hierarchical structured format"
            },
            {
                "name": "custom",
                "description": "Custom template with placeholders"
            }
        ]
    }
