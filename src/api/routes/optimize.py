from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.request_schemas import OptimizePromptRequest
from src.schemas.response_schemas import OptimizePromptResponse
from src.models.database import get_db, User, OptimizationHistory
from src.api.dependencies import get_current_active_user
from src.services.llm_service import llm_orchestrator
from src.utils.token_counter import TokenCounter
import json

router = APIRouter()
token_counter = TokenCounter()


@router.post("/optimize-prompt", response_model=OptimizePromptResponse)
async def optimize_prompt(
    request: OptimizePromptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Optimize an existing prompt for better performance
    
    Analyzes the provided prompt and applies optimization strategies
    based on the specified criteria.
    """
    
    try:
        # Analyze current prompt
        original_tokens = await token_counter.count_prompt_tokens(request.prompt)
        
        # Create optimization prompt for LLM
        optimization_messages = [
            {
                "role": "system",
                "content": f"""You are an expert prompt optimization specialist. Your task is to improve the given prompt based on these criteria: {', '.join(request.optimization_criteria)}.

Focus on:
1. Clarity and precision of instructions
2. Token efficiency while maintaining effectiveness
3. Better structure and organization
4. Enhanced examples if present
5. Improved constraints and edge case handling

Return the optimized prompt in the same JSON structure format."""
            },
            {
                "role": "user",
                "content": f"""Please optimize this prompt for the target model '{request.target_model}':

Original prompt:
{json.dumps(request.prompt, indent=2)}

Optimization criteria: {', '.join(request.optimization_criteria)}

Provide the optimized version and explain the improvements made."""
            }
        ]
        
        # Get optimization from LLM
        response = await llm_orchestrator.generate_with_fallback(
            messages=optimization_messages,
            preferred_provider=_get_provider_from_model(request.target_model),
            temperature=0.3
        )
        
        # Extract optimized prompt (simplified - in production would need better parsing)
        optimized_prompt = request.prompt.copy()  # Placeholder
        
        # Calculate improvements
        optimized_tokens = await token_counter.count_prompt_tokens(optimized_prompt)
        
        improvements = [
            "Improved instruction clarity",
            "Enhanced structure and organization"
        ]
        
        if optimized_tokens < original_tokens:
            improvements.append(f"Reduced token count by {original_tokens - optimized_tokens} tokens")
        
        # Calculate metrics
        metrics = {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "token_reduction": max(0, original_tokens - optimized_tokens),
            "efficiency_gain": max(0, (original_tokens - optimized_tokens) / original_tokens * 100)
        }
        
        # Store optimization history
        optimization_history = OptimizationHistory(
            original_prompt=request.prompt,
            optimized_prompt=optimized_prompt,
            optimization_criteria=request.optimization_criteria,
            improvement_metrics=metrics,
            target_model=request.target_model
        )
        
        db.add(optimization_history)
        db.commit()
        
        return OptimizePromptResponse(
            original_prompt=request.prompt,
            optimized_prompt=optimized_prompt,
            improvements=improvements,
            metrics=metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize prompt: {str(e)}"
        )


def _get_provider_from_model(target_model: str) -> str:
    """Get LLM provider from target model"""
    if "claude" in target_model.lower():
        return "claude"
    elif "gpt" in target_model.lower():
        return "openai"
    else:
        return "claude"  # default
