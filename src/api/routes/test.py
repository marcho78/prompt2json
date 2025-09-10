from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.request_schemas import TestPromptRequest
from src.schemas.response_schemas import TestPromptResponse
from src.models.database import get_db, User, PromptTest
from src.api.dependencies import get_current_active_user
import uuid
import time

router = APIRouter()


@router.post("/test-prompt", response_model=TestPromptResponse)
async def test_prompt(
    request: TestPromptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test a prompt with sample input"""
    
    try:
        test_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Simulate prompt execution (in production, this would use the actual LLM)
        actual_output = f"Test output for: {request.test_input}"
        result = "pass"
        
        execution_time = time.time() - start_time
        
        return TestPromptResponse(
            test_id=test_id,
            result=result,
            execution_time=execution_time,
            actual_output=actual_output,
            token_usage=150,
            errors=[]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test prompt: {str(e)}"
        )
