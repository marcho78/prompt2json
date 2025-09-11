#!/usr/bin/env python3
"""
Debug script to reproduce prompt generation issue
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.prompt_generator import PromptGenerator
from src.schemas.request_schemas import GeneratePromptRequest, TargetLLM, Complexity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_prompt_generation():
    """Test prompt generation with detailed logging"""
    
    print("🔍 Starting prompt generation debug test...")
    
    # Create request
    request = GeneratePromptRequest(
        description="Create a chatbot that helps with customer support",
        target_llm=TargetLLM.CLAUDE,
        complexity=Complexity.SIMPLE
    )
    
    print(f"📝 Request: {request.description}")
    print(f"🎯 Target LLM: {request.target_llm}")
    print(f"📊 Complexity: {request.complexity}")
    
    # Create generator
    generator = PromptGenerator()
    
    try:
        print("\n🚀 Starting generation...")
        result = await generator.generate_prompt(request)
        print("✅ Generation completed successfully!")
        print(f"📄 Result type: {type(result)}")
        print(f"📊 Task: {result.task}")
        return result
        
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        print(f"🔍 Error type: {type(e)}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    result = asyncio.run(test_prompt_generation())
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
