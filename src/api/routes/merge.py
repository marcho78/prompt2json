from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.request_schemas import MergePromptsRequest, MergeStrategy
from src.schemas.response_schemas import MergePromptsResponse
from src.api.dependencies import get_current_active_user

router = APIRouter()


@router.post("/merge-prompts", response_model=MergePromptsResponse)
async def merge_prompts(
    request: MergePromptsRequest,
    current_user = Depends(get_current_active_user)
):
    """Combine multiple prompts using specified merge strategy"""
    
    try:
        if len(request.prompts) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 prompts are required for merging"
            )
        
        merged_prompt = {}
        
        if request.merge_strategy == MergeStrategy.SEQUENTIAL:
            merged_prompt = _merge_sequential(request.prompts)
        elif request.merge_strategy == MergeStrategy.PARALLEL:
            merged_prompt = _merge_parallel(request.prompts)
        elif request.merge_strategy == MergeStrategy.CONDITIONAL:
            merged_prompt = _merge_conditional(request.prompts)
        else:
            merged_prompt = _merge_sequential(request.prompts)  # default
        
        metadata = {
            "merge_timestamp": "2023-01-01T00:00:00Z",
            "source_prompts_count": len(request.prompts),
            "strategy_used": request.merge_strategy.value
        }
        
        return MergePromptsResponse(
            merged_prompt=merged_prompt,
            merge_strategy=request.merge_strategy.value,
            components_count=len(request.prompts),
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge prompts: {str(e)}"
        )


def _merge_sequential(prompts: list) -> dict:
    """Merge prompts sequentially"""
    merged = prompts[0].copy()
    
    # Combine instructions
    all_instructions = []
    for prompt in prompts:
        if prompt.get("instructions") and prompt["instructions"].get("steps"):
            all_instructions.extend(prompt["instructions"]["steps"])
    
    if all_instructions and merged.get("instructions"):
        merged["instructions"]["steps"] = all_instructions
    
    # Combine examples
    all_examples = []
    for prompt in prompts:
        if prompt.get("examples"):
            all_examples.extend(prompt["examples"])
    
    merged["examples"] = all_examples
    
    return merged


def _merge_parallel(prompts: list) -> dict:
    """Merge prompts for parallel execution"""
    merged = {
        "task": "parallel_execution",
        "subtasks": prompts,
        "instructions": {
            "primary_goal": "Execute multiple tasks in parallel",
            "steps": [
                "Process each subtask independently",
                "Combine results as specified"
            ]
        }
    }
    
    return merged


def _merge_conditional(prompts: list) -> dict:
    """Merge prompts with conditional logic"""
    merged = {
        "task": "conditional_execution", 
        "conditions": [
            {
                "condition": f"condition_{i+1}",
                "prompt": prompt
            }
            for i, prompt in enumerate(prompts)
        ],
        "instructions": {
            "primary_goal": "Execute prompts based on conditions",
            "steps": [
                "Evaluate conditions in order",
                "Execute first matching prompt",
                "Return appropriate result"
            ]
        }
    }
    
    return merged
