from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from src.config import settings
from src.schemas.request_schemas import GeneratePromptRequest
from src.schemas.response_schemas import GeneratePromptResponse, PromptMetadata
from src.models.database import get_db, GeneratedPrompt, User
from src.api.dependencies_optional import get_current_user_optional
from src.services.prompt_generator import PromptGenerator
from src.utils.token_counter import TokenCounter
from src.middleware.rate_limiter import apply_rate_limit, add_rate_limit_headers

router = APIRouter()
prompt_generator = PromptGenerator()
token_counter = TokenCounter()


@router.post("/generate-prompt")
async def generate_prompt(
    prompt_request: GeneratePromptRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Generate a structured JSON prompt from natural language description
    
    This endpoint analyzes the user's natural language description and creates
    a comprehensive, structured prompt optimized for the target LLM.
    """
    
    try:
        # Estimate tokens for this request
        estimated_tokens = await _estimate_request_tokens(prompt_request)
        
        # Apply rate limiting
        user_id = str(current_user.id) if current_user else None
        usage_stats = await apply_rate_limit(
            request=request,
            estimated_tokens=estimated_tokens,
            user_id=user_id,
            endpoint="generate-prompt"
        )
        
        # Generate the prompt structure
        prompt_structure = await prompt_generator.generate_prompt(prompt_request)
        
        # Convert to dict for response and storage
        try:
            prompt_dict = prompt_structure.dict() if hasattr(prompt_structure, 'dict') else prompt_structure.__dict__
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to serialize prompt structure: {str(e)}"
            )
        
        # Calculate additional metadata
        complexity_score = _calculate_complexity_score(prompt_structure)
        suggestions = _generate_suggestions(prompt_structure, prompt_request)
        
        # Create metadata for response
        metadata = PromptMetadata(
            estimated_tokens=prompt_structure.metadata.estimated_tokens,
            complexity_score=complexity_score,
            suggestions=suggestions,
            version=prompt_structure.metadata.version,
            created_at=prompt_structure.metadata.created_at,
            target_models=prompt_structure.metadata.target_models
        )
        
        # Store the generated prompt in database (only for registered users)
        if current_user:
            db_prompt = GeneratedPrompt(
                user_id=current_user.id,
                description=prompt_request.description,
                target_llm=prompt_request.target_llm.value,
                complexity=prompt_request.complexity.value,
                prompt_data=prompt_dict,
                prompt_metadata=metadata.dict(),
                optimization_goals=[goal.value for goal in prompt_request.optimization_goals]
            )
            
            db.add(db_prompt)
            db.commit()
            db.refresh(db_prompt)
        
        # Create response with rate limiting info
        response_data = {
            'prompt': prompt_dict,
            'metadata': metadata.dict(),
            'rate_limit_info': {
                'requests_remaining': usage_stats['usage']['requests_remaining'],
                'tokens_remaining': usage_stats['usage']['tokens_remaining'],
                'user_type': usage_stats['user_type']
            }
        }
        
        # Add warnings if near limits
        if usage_stats['warnings']['near_request_limit'] or usage_stats['warnings']['near_token_limit']:
            response_data['warnings'] = []
            if usage_stats['warnings']['near_request_limit']:
                response_data['warnings'].append(f"You've used {usage_stats['warnings']['request_usage_percent']}% of your daily requests")
            if usage_stats['warnings']['near_token_limit']:
                response_data['warnings'].append(f"You've used {usage_stats['warnings']['token_usage_percent']}% of your daily tokens")
        
        response = JSONResponse(content=response_data)
        return add_rate_limit_headers(response, usage_stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate prompt: {str(e)}"
        )


def _calculate_complexity_score(prompt_structure) -> float:
    """Calculate complexity score based on prompt structure"""
    
    score = 0.0
    
    # Base complexity from instructions
    if prompt_structure.instructions and prompt_structure.instructions.steps:
        score += len(prompt_structure.instructions.steps) * 0.1
    
    # Complexity from examples
    if prompt_structure.examples:
        score += len(prompt_structure.examples) * 0.15
    
    # Complexity from constraints
    if prompt_structure.constraints:
        score += len(prompt_structure.constraints) * 0.1
    
    # Complexity from edge cases
    if prompt_structure.edge_cases:
        score += len(prompt_structure.edge_cases) * 0.1
    
    # Complexity from components
    if prompt_structure.components:
        if prompt_structure.components.chain_of_thought and prompt_structure.components.chain_of_thought.enabled:
            score += 0.2
        if prompt_structure.components.few_shot_learning:
            score += 0.15
        if prompt_structure.components.output_validation:
            score += 0.1
    
    # Cap at 1.0
    return min(1.0, score)


def _generate_suggestions(prompt_structure, request: GeneratePromptRequest) -> list:
    """Generate improvement suggestions"""
    
    suggestions = []
    
    # Check if examples are missing but could be helpful
    if not prompt_structure.examples and not request.include_examples:
        suggestions.append("Consider adding examples to improve clarity and accuracy")
    
    # Check if constraints are minimal
    if not prompt_structure.constraints:
        suggestions.append("Adding constraints could help prevent edge cases and improve output consistency")
    
    # Check token efficiency
    if prompt_structure.metadata.estimated_tokens > 3000:
        suggestions.append("Consider optimizing for token efficiency to reduce API costs")
    
    # Check complexity vs target
    complexity_score = _calculate_complexity_score(prompt_structure)
    if complexity_score < 0.3 and request.complexity.value == "complex":
        suggestions.append("Prompt structure could be more complex for the requested complexity level")
    
    return suggestions


async def _estimate_request_tokens(request: GeneratePromptRequest) -> int:
    """Estimate tokens needed for this request based on complexity and input length"""
    
    base_tokens = {
        "simple": 1500,
        "moderate": 3000, 
        "complex": 5000
    }
    
    # Base estimation from complexity
    estimated = base_tokens.get(request.complexity.value, 2000)
    
    # Adjust based on description length
    description_tokens = len(request.description) // 4  # Rough char-to-token ratio
    estimated += description_tokens
    
    # Add extra tokens if examples are requested
    if request.include_examples:
        estimated += 1000
    
    # Add tokens for optimization goals
    estimated += len(request.optimization_goals) * 200
    
    return min(estimated, settings.REGISTERED_MAX_TOKENS_PER_REQUEST)
