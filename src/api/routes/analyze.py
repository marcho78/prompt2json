from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.request_schemas import AnalyzePromptRequest
from src.schemas.response_schemas import AnalyzePromptResponse, QualityIssue
from src.api.dependencies import get_current_active_user
from src.utils.token_counter import TokenCounter

router = APIRouter()
token_counter = TokenCounter()


@router.post("/analyze-prompt", response_model=AnalyzePromptResponse)
async def analyze_prompt(
    request: AnalyzePromptRequest,
    current_user = Depends(get_current_active_user)
):
    """Analyze prompt quality and effectiveness"""
    
    try:
        # Calculate quality score
        quality_score = await _calculate_quality_score(request.prompt)
        
        # Identify issues
        issues = await _identify_issues(request.prompt)
        
        # Generate improvements
        improvements = _generate_improvements(request.prompt, issues)
        
        # Calculate metrics
        metrics = await _calculate_metrics(request.prompt)
        
        return AnalyzePromptResponse(
            quality_score=quality_score,
            issues=issues,
            improvements=improvements,
            metrics=metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze prompt: {str(e)}"
        )


async def _calculate_quality_score(prompt: dict) -> float:
    """Calculate overall quality score"""
    score = 0.5  # Base score
    
    # Check for instructions
    if prompt.get("instructions"):
        score += 0.2
    
    # Check for examples
    if prompt.get("examples"):
        score += 0.15
    
    # Check for constraints
    if prompt.get("constraints"):
        score += 0.1
    
    # Check for clear output format
    if prompt.get("output_format"):
        score += 0.05
    
    return min(1.0, score)


async def _identify_issues(prompt: dict) -> list:
    """Identify quality issues in the prompt"""
    issues = []
    
    if not prompt.get("instructions"):
        issues.append(QualityIssue(
            type="missing_instructions",
            severity="high",
            description="Prompt lacks clear instructions",
            suggestion="Add detailed step-by-step instructions"
        ))
    
    if not prompt.get("examples"):
        issues.append(QualityIssue(
            type="missing_examples",
            severity="medium",
            description="No examples provided",
            suggestion="Add examples to clarify expected output"
        ))
    
    return issues


def _generate_improvements(prompt: dict, issues: list) -> list:
    """Generate improvement suggestions"""
    improvements = []
    
    for issue in issues:
        improvements.append(issue.suggestion)
    
    improvements.append("Consider adding edge cases and constraints")
    improvements.append("Optimize token usage while maintaining clarity")
    
    return improvements


async def _calculate_metrics(prompt: dict) -> dict:
    """Calculate detailed metrics"""
    estimated_tokens = await token_counter.count_prompt_tokens(prompt)
    
    return {
        "estimated_tokens": estimated_tokens,
        "instruction_clarity": 0.8,
        "structure_quality": 0.7,
        "example_quality": 0.6 if prompt.get("examples") else 0.0
    }
