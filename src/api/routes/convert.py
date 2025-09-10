from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.request_schemas import ConvertPromptRequest
from src.schemas.response_schemas import ConvertPromptResponse
from src.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("/convert-prompt", response_model=ConvertPromptResponse)
async def convert_prompt(
    request: ConvertPromptRequest,
    current_user = Depends(get_current_active_user)
):
    """Convert prompt between different LLM formats"""
    
    try:
        # Basic conversion logic (simplified for demo)
        converted_prompt = request.prompt.copy()
        
        # Add format-specific adjustments
        conversion_notes = []
        
        if request.source_format.lower() == "openai" and request.target_format.lower() == "anthropic":
            conversion_notes.append("Converted system message format for Claude")
            conversion_notes.append("Adjusted message structure for Anthropic API")
        elif request.source_format.lower() == "anthropic" and request.target_format.lower() == "openai":
            conversion_notes.append("Adapted for OpenAI chat completion format")
            conversion_notes.append("Restructured system message for GPT models")
        
        return ConvertPromptResponse(
            converted_prompt=converted_prompt,
            source_format=request.source_format,
            target_format=request.target_format,
            conversion_notes=conversion_notes
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert prompt: {str(e)}"
        )
