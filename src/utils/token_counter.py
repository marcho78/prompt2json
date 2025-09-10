from typing import Dict, Any, Optional
import json
import re


class TokenCounter:
    """Utility for counting tokens in text for different LLM providers"""
    
    def __init__(self):
        self._tiktoken_available = False
        try:
            import tiktoken
            self._tiktoken = tiktoken
            self._tiktoken_available = True
        except ImportError:
            pass
    
    async def count_tokens(self, text: str, provider: str = "claude") -> int:
        """Count tokens in text for specific provider"""
        
        if provider.lower() in ["claude", "anthropic"]:
            return await self.count_claude_tokens(text)
        elif provider.lower() in ["openai", "gpt-4", "gpt-3.5"]:
            return await self.count_openai_tokens(text)
        else:
            # Default estimation
            return self.estimate_tokens(text)
    
    async def count_claude_tokens(self, text: str) -> int:
        """Count tokens for Claude models"""
        # Claude uses a similar tokenization to GPT models
        # Rough estimation: ~4 characters per token for English text
        return max(1, len(text) // 4)
    
    async def count_openai_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens for OpenAI models using tiktoken if available"""
        
        if not self._tiktoken_available:
            return self.estimate_tokens(text)
        
        try:
            # Get the appropriate encoding for the model
            if "gpt-4" in model.lower():
                encoding = self._tiktoken.get_encoding("cl100k_base")
            elif "gpt-3.5" in model.lower():
                encoding = self._tiktoken.get_encoding("cl100k_base")
            else:
                encoding = self._tiktoken.get_encoding("cl100k_base")
            
            return len(encoding.encode(text))
            
        except Exception:
            return self.estimate_tokens(text)
    
    def estimate_tokens(self, text: str) -> int:
        """Basic token estimation as fallback"""
        # Remove extra whitespace and count
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        
        # Rough estimation: 
        # - ~4 characters per token for English text
        # - Adjust for code, JSON, and special characters
        char_count = len(cleaned_text)
        
        # Count special tokens (punctuation, brackets, etc.)
        special_chars = len(re.findall(r'[{}()\[\].,;:!?"\'-]', text))
        
        # Estimate tokens
        estimated_tokens = (char_count // 4) + (special_chars // 2)
        
        return max(1, estimated_tokens)
    
    async def count_prompt_tokens(self, prompt_structure: Dict[str, Any]) -> int:
        """Count tokens in a complete prompt structure"""
        
        total_tokens = 0
        
        # Convert prompt to text representation
        prompt_text = self._prompt_to_text(prompt_structure)
        
        # Count tokens in the full prompt
        total_tokens = await self.count_tokens(prompt_text)
        
        return total_tokens
    
    def _prompt_to_text(self, prompt_structure: Dict[str, Any]) -> str:
        """Convert prompt structure to text for token counting"""
        
        text_parts = []
        
        # System message
        if "system_message" in prompt_structure and prompt_structure["system_message"]:
            text_parts.append(f"System: {prompt_structure['system_message']}")
        
        # Instructions
        if "instructions" in prompt_structure:
            instructions = prompt_structure["instructions"]
            if isinstance(instructions, dict):
                if "primary_goal" in instructions:
                    text_parts.append(f"Goal: {instructions['primary_goal']}")
                if "steps" in instructions:
                    steps_text = " ".join(instructions["steps"])
                    text_parts.append(f"Steps: {steps_text}")
                if "context" in instructions and instructions["context"]:
                    text_parts.append(f"Context: {instructions['context']}")
        
        # Input/Output format descriptions
        if "input_format" in prompt_structure:
            input_format = prompt_structure["input_format"]
            if isinstance(input_format, dict) and "description" in input_format:
                text_parts.append(f"Input: {input_format['description']}")
        
        if "output_format" in prompt_structure:
            output_format = prompt_structure["output_format"]
            if isinstance(output_format, dict):
                text_parts.append(f"Output format: {json.dumps(output_format, indent=2)}")
        
        # Examples
        if "examples" in prompt_structure and prompt_structure["examples"]:
            for i, example in enumerate(prompt_structure["examples"][:3]):  # Limit to 3 examples
                if isinstance(example, dict):
                    example_text = f"Example {i+1}: Input: {example.get('input', '')}, Output: {example.get('output', '')}"
                    if "explanation" in example and example["explanation"]:
                        example_text += f", Explanation: {example['explanation']}"
                    text_parts.append(example_text)
        
        # Constraints
        if "constraints" in prompt_structure and prompt_structure["constraints"]:
            constraints_text = " ".join(prompt_structure["constraints"])
            text_parts.append(f"Constraints: {constraints_text}")
        
        # Edge cases
        if "edge_cases" in prompt_structure and prompt_structure["edge_cases"]:
            edge_cases_text = " ".join(prompt_structure["edge_cases"])
            text_parts.append(f"Edge cases: {edge_cases_text}")
        
        return " ".join(text_parts)
    
    def get_token_stats(self, text: str) -> Dict[str, Any]:
        """Get detailed token statistics"""
        
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        estimated_tokens = self.estimate_tokens(text)
        
        return {
            "character_count": char_count,
            "word_count": word_count,
            "line_count": line_count,
            "estimated_tokens": estimated_tokens,
            "chars_per_token": char_count / max(1, estimated_tokens)
        }
