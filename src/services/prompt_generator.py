from typing import Dict, Any, List, Optional
import json
import re
import logging
from datetime import datetime
from src.schemas.request_schemas import GeneratePromptRequest, TargetLLM, Complexity
from src.schemas.prompt_schemas import (
    PromptStructure, Instructions, InputFormat, OutputFormat, 
    Example, PromptMetadata, PromptComponent, ChainOfThought, FewShotLearning
)
from src.services.llm_service import llm_orchestrator
from src.utils.token_counter import TokenCounter


class PromptGenerator:
    """Core prompt generation service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.token_counter = TokenCounter()
        self.templates = self._load_templates()
    
    async def generate_prompt(self, request: GeneratePromptRequest) -> PromptStructure:
        """Generate a structured prompt from natural language description"""
        
        # Parse the natural language description
        parsed_intent = await self._parse_description(request.description)
        
        # Generate the prompt structure
        prompt = await self._build_prompt_structure(
            parsed_intent=parsed_intent,
            target_llm=request.target_llm,
            complexity=request.complexity,
            include_examples=request.include_examples,
            optimization_goals=request.optimization_goals
        )
        
        return prompt
    
    async def _parse_description(self, description: str) -> Dict[str, Any]:
        """Parse natural language description to extract intent and structure"""
        
        self.logger.info(f"Starting _parse_description with description length: {len(description)}")
        
        # Create a prompt for the LLM to parse the user's description
        parsing_messages = [
            {
                "role": "system",
                "content": """You are an expert prompt engineer. Analyze the user's description and extract structured information about their prompt requirements.

Extract the following information:
1. Task type (data_extraction, code_generation, analysis, creative_writing, classification, etc.)
2. Input format and constraints
3. Output format and structure
4. Key requirements and constraints
5. Suggested examples
6. Edge cases to consider

Return your analysis as a JSON object with these fields."""
            },
            {
                "role": "user", 
                "content": f"""Please analyze this prompt description and extract structured information:

"{description}"

Provide a detailed analysis in JSON format with task_type, input_format, output_format, requirements, examples, and edge_cases."""
            }
        ]
        
        try:
            self.logger.info("Attempting LLM parsing of description")
            response = await llm_orchestrator.generate_with_fallback(
                messages=parsing_messages,
                temperature=0.3  # Lower temperature for more consistent parsing
            )
            
            self.logger.info(f"LLM response received, length: {len(response.get('text', ''))}")
            
            # Try to extract JSON from the response
            parsed_response = self._extract_json(response["text"])
            if parsed_response:
                self.logger.info("Successfully parsed JSON from LLM response")
                return parsed_response
            else:
                self.logger.warning("Could not extract JSON from LLM response, falling back to pattern extraction")
                # Fallback to basic pattern extraction
                return self._extract_basic_patterns(description)
                
        except Exception as e:
            self.logger.error(f"LLM parsing failed with error: {str(e)}, falling back to pattern extraction")
            # Fallback to basic pattern extraction
            return self._extract_basic_patterns(description)
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON without markdown
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
                
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _extract_basic_patterns(self, description: str) -> Dict[str, Any]:
        """Basic pattern extraction as fallback"""
        
        self.logger.info("Using basic pattern extraction fallback")
        description_lower = description.lower()
        
        # Determine task type based on keywords
        task_type = "general"
        if any(word in description_lower for word in ["extract", "parse", "identify"]):
            task_type = "data_extraction"
        elif any(word in description_lower for word in ["generate", "create", "write code"]):
            task_type = "code_generation"
        elif any(word in description_lower for word in ["analyze", "examine", "review"]):
            task_type = "analysis"
        elif any(word in description_lower for word in ["classify", "categorize", "sort"]):
            task_type = "classification"
        elif any(word in description_lower for word in ["write", "story", "creative"]):
            task_type = "creative_writing"
        
        result = {
            "task_type": task_type,
            "input_format": {
                "type": "string",
                "description": "Input text to process",
                "constraints": []
            },
            "output_format": {
                "type": "object",
                "description": "Structured output based on task requirements"
            },
            "requirements": [description],
            "examples": [],
            "edge_cases": []
        }
        
        self.logger.info(f"Basic pattern extraction completed, task_type: {task_type}")
        return result
    
    async def _build_prompt_structure(
        self, 
        parsed_intent: Dict[str, Any],
        target_llm: TargetLLM,
        complexity: Complexity,
        include_examples: bool,
        optimization_goals: List[str]
    ) -> PromptStructure:
        """Build the structured prompt from parsed intent"""
        
        self.logger.info(f"Starting _build_prompt_structure with task_type: {parsed_intent.get('task_type', 'general')}")
        task_type = parsed_intent.get("task_type", "general")
        
        # Build instructions
        instructions = Instructions(
            primary_goal=self._generate_primary_goal(parsed_intent),
            steps=self._generate_steps(parsed_intent, complexity),
            context=self._generate_context(parsed_intent, target_llm)
        )
        
        # Build input/output formats
        input_format = self._build_input_format(parsed_intent)
        output_format = self._build_output_format(parsed_intent)
        
        # Generate examples if requested
        examples = []
        if include_examples:
            examples = await self._generate_examples(parsed_intent, input_format, output_format)
        
        # Build advanced components based on complexity
        components = None
        if complexity in [Complexity.MODERATE, Complexity.COMPLEX]:
            components = self._build_components(parsed_intent, complexity, include_examples)
        
        # Create metadata
        self.logger.info("Building prompt dictionary for token counting")
        prompt_dict = {
            "task": task_type,
            "instructions": instructions.dict(),
            "input_format": input_format.dict(),
            "output_format": output_format.dict(),
            "examples": [ex.dict() for ex in examples]
        }
        
        self.logger.info(f"Starting token counting for prompt_dict with {len(json.dumps(prompt_dict))} characters")
        try:
            estimated_tokens = await self.token_counter.count_tokens(json.dumps(prompt_dict))
            self.logger.info(f"Token counting completed: {estimated_tokens} tokens")
        except Exception as e:
            self.logger.error(f"Token counting failed: {str(e)}")
            estimated_tokens = 0
        
        self.logger.info("Creating PromptMetadata")
        try:
            metadata = PromptMetadata(
                version="1.0",
                created_at=datetime.utcnow(),
                target_models=[target_llm.value],
                estimated_tokens=estimated_tokens
            )
            self.logger.info("PromptMetadata created successfully")
        except Exception as e:
            self.logger.error(f"PromptMetadata creation failed: {str(e)}")
            raise
        
        self.logger.info("Creating final PromptStructure")
        try:
            # Handle constraints and edge_cases that might be strings
            constraints = parsed_intent.get("constraints", [])
            if isinstance(constraints, str):
                constraints = [constraints]
            elif not isinstance(constraints, list):
                constraints = []
            
            edge_cases = parsed_intent.get("edge_cases", [])
            if isinstance(edge_cases, str):
                edge_cases = [edge_cases]
            elif not isinstance(edge_cases, list):
                edge_cases = []
            
            result = PromptStructure(
                task=task_type,
                system_message=self._generate_system_message(parsed_intent, target_llm),
                instructions=instructions,
                input_format=input_format,
                output_format=output_format,
                examples=examples,
                constraints=constraints,
                edge_cases=edge_cases,
                components=components,
                metadata=metadata
            )
            self.logger.info("PromptStructure created successfully")
            return result
        except Exception as e:
            self.logger.error(f"PromptStructure creation failed: {str(e)}")
            raise
    
    def _generate_primary_goal(self, parsed_intent: Dict[str, Any]) -> str:
        """Generate primary goal from parsed intent"""
        requirements = parsed_intent.get("requirements", [])
        if requirements:
            return requirements[0]
        
        task_type = parsed_intent.get("task_type", "general")
        return f"Complete the {task_type} task according to the specified requirements"
    
    def _generate_steps(self, parsed_intent: Dict[str, Any], complexity: Complexity) -> List[str]:
        """Generate step-by-step instructions"""
        
        task_type = parsed_intent.get("task_type", "general")
        
        base_steps = [
            "Carefully read and understand the input",
            "Process the input according to the task requirements",
            "Generate the output in the specified format"
        ]
        
        # Add complexity-specific steps
        if complexity == Complexity.COMPLEX:
            if task_type == "data_extraction":
                return [
                    "Analyze the input text structure and content",
                    "Identify all relevant entities and relationships",
                    "Extract data points according to the schema",
                    "Validate extracted data for completeness and accuracy",
                    "Format the output according to specifications"
                ]
            elif task_type == "analysis":
                return [
                    "Examine the input data comprehensively",
                    "Identify patterns, trends, and anomalies",
                    "Apply relevant analytical frameworks",
                    "Generate insights and conclusions",
                    "Provide actionable recommendations"
                ]
        
        return base_steps
    
    def _generate_context(self, parsed_intent: Dict[str, Any], target_llm: TargetLLM) -> Optional[str]:
        """Generate context based on task and target LLM"""
        
        task_type = parsed_intent.get("task_type", "general")
        
        contexts = {
            "data_extraction": "Focus on accuracy and completeness. Extract all relevant information without making assumptions.",
            "analysis": "Provide thorough and objective analysis. Support conclusions with evidence from the input.",
            "code_generation": "Write clean, efficient, and well-documented code. Follow best practices.",
            "classification": "Be precise and consistent in classifications. Explain reasoning when uncertain.",
            "creative_writing": "Be creative while maintaining coherence and meeting specified requirements."
        }
        
        return contexts.get(task_type)
    
    def _build_input_format(self, parsed_intent: Dict[str, Any]) -> InputFormat:
        """Build input format specification"""
        
        input_spec = parsed_intent.get("input_format", {})
        
        # Handle constraints that might be strings or lists
        constraints = input_spec.get("constraints", [])
        if isinstance(constraints, str):
            # Convert string to list with single item
            constraints = [constraints]
        elif not isinstance(constraints, list):
            # Fallback for other types
            constraints = []
        
        return InputFormat(
            type=input_spec.get("type", "string"),
            description=input_spec.get("description", "Input data to process"),
            constraints=constraints
        )
    
    def _build_output_format(self, parsed_intent: Dict[str, Any]) -> OutputFormat:
        """Build output format specification"""
        
        output_spec = parsed_intent.get("output_format", {})
        
        # Handle required fields that might be strings or lists
        required = output_spec.get("required", [])
        if isinstance(required, str):
            # Convert string to list with single item
            required = [required]
        elif not isinstance(required, list):
            # Fallback for other types
            required = []
        
        return OutputFormat(
            type=output_spec.get("type", "object"),
            properties=output_spec.get("properties"),
            required=required
        )
    
    async def _generate_examples(
        self, 
        parsed_intent: Dict[str, Any], 
        input_format: InputFormat, 
        output_format: OutputFormat
    ) -> List[Example]:
        """Generate examples for the prompt"""
        
        # For now, return basic examples
        # In a full implementation, this could use the LLM to generate realistic examples
        
        examples: List[Example] = []
        suggested_examples = parsed_intent.get("examples", [])

        # Normalize examples to a list of mappings
        if isinstance(suggested_examples, dict):
            suggested_list = [suggested_examples]
        elif isinstance(suggested_examples, list):
            suggested_list = suggested_examples
        else:
            suggested_list = []

        for ex in suggested_list[:3]:  # Limit to 3 examples
            if isinstance(ex, dict):
                examples.append(Example(
                    input=ex.get("input", "Sample input"),
                    output=ex.get("output", "Sample output"),
                    explanation=ex.get("explanation")
                ))

        return examples
    
    def _build_components(
        self, 
        parsed_intent: Dict[str, Any], 
        complexity: Complexity, 
        include_examples: bool
    ) -> PromptComponent:
        """Build advanced prompt components"""
        
        components = PromptComponent()
        
        # Add chain of thought for complex tasks
        if complexity == Complexity.COMPLEX:
            components.chain_of_thought = ChainOfThought(
                enabled=True,
                steps=[
                    "Think step by step",
                    "Explain your reasoning",
                    "Verify your conclusions"
                ]
            )
        
        # Add few-shot learning if examples are included
        if include_examples:
            components.few_shot_learning = FewShotLearning(
                examples=[],  # Examples are handled separately
                example_selection="diverse"
            )
        
        return components
    
    def _generate_system_message(self, parsed_intent: Dict[str, Any], target_llm: TargetLLM) -> str:
        """Generate appropriate system message for the target LLM"""
        
        task_type = parsed_intent.get("task_type", "general")
        
        system_messages = {
            "data_extraction": "You are an expert data extraction specialist with precise analytical skills.",
            "code_generation": "You are a senior software engineer with expertise in multiple programming languages.",
            "analysis": "You are a skilled analyst capable of extracting insights from complex information.",
            "classification": "You are an expert classifier with strong pattern recognition abilities.",
            "creative_writing": "You are a creative writer with excellent storytelling abilities."
        }
        
        base_message = system_messages.get(task_type, "You are a helpful AI assistant.")
        
        # Add LLM-specific adjustments
        if target_llm == TargetLLM.CLAUDE:
            return f"{base_message} Provide thoughtful and detailed responses."
        elif target_llm == TargetLLM.GPT_4:
            return f"{base_message} Be precise and comprehensive in your responses."
        
        return base_message
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load prompt templates"""
        # This would load from a templates file in a full implementation
        return {}
