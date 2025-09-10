# AI JSON Prompt Generator API - Complete Documentation

## 📖 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints](#api-endpoints)
6. [Error Handling](#error-handling)
7. [Integration Examples](#integration-examples)
8. [SDKs and Libraries](#sdks-and-libraries)
9. [Best Practices](#best-practices)

---

## Overview

The AI JSON Prompt Generator API is a comprehensive FastAPI application that converts natural language descriptions into structured JSON prompts optimized for Large Language Models (LLMs). The API supports both anonymous and registered users with intelligent rate limiting and usage tracking.

### Base URL
```
http://127.0.0.1:8000  (Development)
https://api.your-domain.com  (Production)
```

### Key Features
- 🧠 Natural language to structured JSON prompts
- 🤖 Multi-LLM support (Claude, GPT-4, Gemini, Llama)
- 👤 Anonymous and authenticated access
- ⚡ Smart rate limiting with daily quotas
- 🔧 Prompt optimization and testing
- 📊 Quality analysis and scoring

---

## Quick Start

### Anonymous Usage (No Registration Required)

Generate your first prompt in seconds:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Analyze customer feedback and categorize by sentiment",
    "target_llm": "claude",
    "complexity": "simple"
  }'
```

### Check Your Usage
```bash
curl "http://127.0.0.1:8000/api/v1/usage"
```

---

## Authentication

### Optional Authentication
The API works with **optional authentication** - you can use most endpoints without registering, but get enhanced limits and features with an account.

### User Registration
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "developer123",
    "email": "dev@example.com", 
    "password": "securePassword123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "developer123",
  "email": "dev@example.com",
  "is_active": true,
  "created_at": "2025-01-10T12:00:00Z"
}
```

### Login & Get JWT Token
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "developer123",
    "password": "securePassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using JWT Token
Include the token in the `Authorization` header:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://127.0.0.1:8000/api/v1/generate-prompt"
```

---

## Rate Limiting

### Usage Tiers

| Feature | Anonymous Users | Registered Users |
|---------|----------------|------------------|
| **Daily Requests** | 10 | 50 |
| **Daily Tokens** | 50,000 | 200,000 |
| **Max Tokens/Request** | 5,000 | 10,000 |
| **Complex Prompts** | ❌ | ✅ |
| **Prompt History** | ❌ | ✅ |

### Rate Limit Headers

Every response includes rate limiting information:

```http
HTTP/1.1 200 OK
X-RateLimit-Type: daily
X-RateLimit-Limit-Requests: 10
X-RateLimit-Remaining-Requests: 7
X-RateLimit-Limit-Tokens: 50000
X-RateLimit-Remaining-Tokens: 42000
X-RateLimit-Reset: 2025-01-11T00:00:00Z
X-RateLimit-User-Type: anonymous
Content-Type: application/json
```

### Rate Limit Errors

#### Daily Request Limit Exceeded (429)
```json
{
  "error": "DAILY_REQUEST_LIMIT_EXCEEDED",
  "message": "You've reached your daily limit of 10 requests. Please try again tomorrow. Register for free to get 5x more usage.",
  "limit": 10,
  "used": 10,
  "reset_time": "2025-01-11T00:00:00Z",
  "upgrade_url": "/auth/register"
}
```

#### Token Limit Exceeded (429)
```json
{
  "error": "DAILY_TOKEN_LIMIT_EXCEEDED",
  "message": "You've used your daily token allowance. Try simpler prompts or wait until tomorrow. Register for free to get 4x more tokens.",
  "limit": 50000,
  "used": 48500,
  "estimated_for_request": 2000,
  "reset_time": "2025-01-11T00:00:00Z",
  "tips": [
    "Use 'simple' complexity for fewer tokens",
    "Optimize your prompts to use fewer tokens",
    "Register for free to get 200,000 daily tokens"
  ]
}
```

---

## API Endpoints

### 🔐 Authentication Endpoints

#### Register User
**POST** `/auth/register`

Create a new user account for enhanced API access.

**Request:**
```json
{
  "username": "string (3-50 chars)",
  "email": "string (valid email)",
  "password": "string (min 8 chars)"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "developer123",
  "email": "dev@example.com",
  "is_active": true,
  "created_at": "2025-01-10T12:00:00Z"
}
```

#### Login
**POST** `/auth/login`

Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
**GET** `/auth/me`

Get information about the current authenticated user.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "id": 1,
  "username": "developer123", 
  "email": "dev@example.com",
  "is_active": true,
  "created_at": "2025-01-10T12:00:00Z"
}
```

#### Refresh Token
**POST** `/auth/refresh`

Generate a new JWT token for authenticated user.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 🧠 Core Prompt Generation Endpoints

#### Generate Prompt
**POST** `/api/v1/generate-prompt`

Generate structured JSON prompts from natural language descriptions.

**Request:**
```json
{
  "description": "string (min 10 chars) - Natural language description",
  "target_llm": "claude | gpt-4 | gemini | llama",
  "complexity": "simple | moderate | complex",
  "include_examples": true,
  "optimization_goals": ["clarity", "efficiency", "accuracy", "token_reduction"]
}
```

**Response:**
```json
{
  "prompt": {
    "task": "analysis",
    "system_message": "You are a skilled analyst...",
    "instructions": {
      "primary_goal": "Analyze customer feedback...",
      "steps": ["Step 1", "Step 2", "Step 3"],
      "context": "Focus on accuracy..."
    },
    "input_format": {
      "type": "string",
      "description": "Customer feedback text",
      "constraints": ["Non-empty text"]
    },
    "output_format": {
      "type": "object",
      "properties": {
        "sentiment": {"type": "string"},
        "score": {"type": "number"}
      },
      "required": ["sentiment", "score"]
    },
    "examples": [
      {
        "input": "Great product!",
        "output": {"sentiment": "positive", "score": 0.9},
        "explanation": "Clear positive sentiment"
      }
    ],
    "constraints": ["Extract only factual information"],
    "edge_cases": ["Handle ambiguous feedback"],
    "components": null,
    "metadata": {
      "version": "1.0",
      "created_at": "2025-01-10T12:00:00Z",
      "target_models": ["claude"],
      "estimated_tokens": 1245
    }
  },
  "metadata": {
    "estimated_tokens": 1245,
    "complexity_score": 0.6,
    "suggestions": ["Consider adding more examples"],
    "version": "1.0",
    "created_at": "2025-01-10T12:00:00Z",
    "target_models": ["claude"]
  },
  "rate_limit_info": {
    "requests_remaining": 9,
    "tokens_remaining": 48755,
    "user_type": "anonymous"
  },
  "warnings": [
    "You've used 80% of your daily tokens"
  ]
}
```

#### Optimize Prompt
**POST** `/api/v1/optimize-prompt`

Optimize existing prompts for better performance and efficiency.

**Request:**
```json
{
  "prompt": {
    "task": "analysis",
    "instructions": {
      "primary_goal": "Analyze sentiment"
    }
  },
  "target_model": "claude",
  "optimization_criteria": ["token_efficiency", "clarity", "accuracy"]
}
```

**Response:**
```json
{
  "original_prompt": { /* original prompt object */ },
  "optimized_prompt": { /* optimized prompt object */ },
  "improvements": [
    "Improved instruction clarity",
    "Reduced token count by 245 tokens",
    "Enhanced structure and organization"
  ],
  "metrics": {
    "original_tokens": 1500,
    "optimized_tokens": 1255,
    "token_reduction": 245,
    "efficiency_gain": 16.3
  }
}
```

#### Convert Prompt
**POST** `/api/v1/convert-prompt`

Convert prompts between different LLM formats (OpenAI ↔ Anthropic ↔ Generic).

**Request:**
```json
{
  "prompt": { /* prompt object */ },
  "source_format": "openai",
  "target_format": "anthropic"
}
```

**Response:**
```json
{
  "converted_prompt": { /* converted prompt object */ },
  "source_format": "openai",
  "target_format": "anthropic",
  "conversion_notes": [
    "Converted system message format for Claude",
    "Adjusted message structure for Anthropic API"
  ]
}
```

#### Test Prompt
**POST** `/api/v1/test-prompt`

Test prompts with sample inputs to validate effectiveness.

**Request:**
```json
{
  "prompt": { /* prompt object */ },
  "test_input": "This product is amazing! I love it.",
  "target_model": "claude"
}
```

**Response:**
```json
{
  "test_id": "test-uuid-1234",
  "result": "pass",
  "execution_time": 1.23,
  "actual_output": "{\"sentiment\": \"positive\", \"score\": 0.95}",
  "expected_output": null,
  "token_usage": 156,
  "errors": []
}
```

#### Analyze Prompt
**POST** `/api/v1/analyze-prompt`

Analyze prompt quality and get improvement suggestions.

**Request:**
```json
{
  "prompt": { /* prompt object */ }
}
```

**Response:**
```json
{
  "quality_score": 0.85,
  "issues": [
    {
      "type": "missing_examples",
      "severity": "medium",
      "description": "No examples provided",
      "suggestion": "Add examples to clarify expected output"
    }
  ],
  "improvements": [
    "Add examples to clarify expected output",
    "Consider adding edge cases and constraints",
    "Optimize token usage while maintaining clarity"
  ],
  "metrics": {
    "estimated_tokens": 1245,
    "instruction_clarity": 0.8,
    "structure_quality": 0.7,
    "example_quality": 0.0
  }
}
```

#### Merge Prompts
**POST** `/api/v1/merge-prompts`

Combine multiple prompts using different strategies.

**Request:**
```json
{
  "prompts": [
    { /* prompt object 1 */ },
    { /* prompt object 2 */ }
  ],
  "merge_strategy": "sequential | parallel | conditional"
}
```

**Response:**
```json
{
  "merged_prompt": { /* combined prompt object */ },
  "merge_strategy": "sequential",
  "components_count": 2,
  "metadata": {
    "merge_timestamp": "2025-01-10T12:00:00Z",
    "source_prompts_count": 2,
    "strategy_used": "sequential"
  }
}
```

---

### 📝 Template Management Endpoints

#### List Templates
**GET** `/api/v1/templates`

Get available prompt templates with optional filtering.

**Query Parameters:**
- `category` (optional): Filter by category
- `complexity` (optional): Filter by complexity level

**Example:**
```bash
curl "http://127.0.0.1:8000/api/v1/templates?category=data_processing&complexity=moderate"
```

**Response:**
```json
{
  "templates": [
    {
      "id": 1,
      "name": "Data Extraction Template",
      "description": "Extract structured data from unstructured text",
      "category": "data_processing",
      "complexity": "moderate", 
      "components": ["entity_recognition", "relationship_mapping"],
      "created_at": "2025-01-10T12:00:00Z"
    }
  ],
  "total_count": 1
}
```

#### Get Template
**GET** `/api/v1/templates/{template_id}`

Get detailed information about a specific template.

**Response:**
```json
{
  "id": 1,
  "name": "Data Extraction Template",
  "description": "Extract structured data from unstructured text",
  "category": "data_processing",
  "complexity": "moderate",
  "components": ["entity_recognition", "relationship_mapping", "data_validation"],
  "created_at": "2025-01-10T12:00:00Z"
}
```

---

### 📈 Usage Monitoring Endpoints

#### Get Usage Statistics
**GET** `/api/v1/usage`

Get comprehensive usage statistics for the current user.

**Response:**
```json
{
  "user_type": "anonymous",
  "daily_limits": {
    "requests": {
      "limit": 10,
      "used": 3,
      "remaining": 7,
      "usage_percent": 30.0
    },
    "tokens": {
      "limit": 50000,
      "used": 12500,
      "remaining": 37500,
      "usage_percent": 25.0
    }
  },
  "per_request_limits": {
    "max_tokens": 5000
  },
  "reset_time": "2025-01-11T00:00:00Z",
  "messages": [
    "You have 7 requests remaining today."
  ],
  "upgrade_benefits": {
    "requests": "50 daily requests (5x more than 10)",
    "tokens": "200,000 daily tokens (4x more than 50,000)",
    "features": [
      "Access to 'complex' prompt generation",
      "Higher per-request token limits",
      "Prompt history and management",
      "Priority support"
    ]
  }
}
```

#### Get Simple Usage
**GET** `/api/v1/usage/simple`

Get essential usage data for frontend components.

**Response:**
```json
{
  "requests_used": 3,
  "requests_limit": 10,
  "tokens_used": 12500,
  "tokens_limit": 50000,
  "user_type": "anonymous",
  "warning_level": "low"
}
```

---

### ❤️ Health & Status Endpoints

#### Health Check
**GET** `/health`

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI JSON Prompt Generator API",
  "version": "1.0.0"
}
```

#### API Info
**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to AI JSON Prompt Generator API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "description": "Generate structured JSON prompts for LLMs from natural language descriptions",
  "endpoints": {
    "authentication": "/auth",
    "generate_prompt": "/api/v1/generate-prompt",
    "optimize_prompt": "/api/v1/optimize-prompt",
    "convert_prompt": "/api/v1/convert-prompt",
    "templates": "/api/v1/templates",
    "test_prompt": "/api/v1/test-prompt",
    "analyze_prompt": "/api/v1/analyze-prompt",
    "merge_prompts": "/api/v1/merge-prompts"
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Authentication required |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `422` | Unprocessable Entity | Validation error |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "detail": "Additional error details",
  "code": 400,
  "timestamp": "2025-01-10T12:00:00Z"
}
```

### Common Errors

#### Validation Error (422)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "description"],
      "msg": "String should have at least 10 characters",
      "input": "short",
      "ctx": {"min_length": 10}
    }
  ]
}
```

#### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials"
}
```

#### Request Too Large (400)
```json
{
  "error": "REQUEST_TOO_LARGE",
  "message": "This request requires 6000 tokens, but limit is 5000.",
  "estimated_tokens": 6000,
  "max_tokens_per_request": 5000,
  "tips": [
    "Try using 'simple' complexity mode",
    "Reduce input text length",
    "Register for free to get higher limits"
  ]
}
```

---

## Integration Examples

### JavaScript/TypeScript

```typescript
class PromptGeneratorClient {
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string, token?: string) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }

  async generatePrompt(request: GeneratePromptRequest): Promise<GeneratePromptResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/generate-prompt`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }

    return response.json();
  }

  async getUsage(): Promise<UsageResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/usage`, {
      headers: this.getHeaders()
    });

    return response.json();
  }
}

// Usage
const client = new PromptGeneratorClient('http://127.0.0.1:8000');

const result = await client.generatePrompt({
  description: 'Analyze customer sentiment from reviews',
  target_llm: 'claude',
  complexity: 'moderate',
  include_examples: true
});

console.log(result.prompt);
```

### Python

```python
import requests
from typing import Optional, Dict, Any

class PromptGeneratorClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def generate_prompt(self, 
                       description: str,
                       target_llm: str = 'claude',
                       complexity: str = 'moderate',
                       include_examples: bool = True,
                       optimization_goals: Optional[list] = None) -> Dict[str, Any]:
        """Generate a structured prompt from natural language description."""
        
        data = {
            'description': description,
            'target_llm': target_llm,
            'complexity': complexity,
            'include_examples': include_examples,
            'optimization_goals': optimization_goals or ['clarity']
        }
        
        response = self.session.post(
            f'{self.base_url}/api/v1/generate-prompt',
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_usage(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        response = self.session.get(f'{self.base_url}/api/v1/usage')
        response.raise_for_status()
        return response.json()
    
    def optimize_prompt(self, prompt: Dict[str, Any], 
                       target_model: str = 'claude',
                       optimization_criteria: Optional[list] = None) -> Dict[str, Any]:
        """Optimize an existing prompt."""
        
        data = {
            'prompt': prompt,
            'target_model': target_model,
            'optimization_criteria': optimization_criteria or ['token_efficiency']
        }
        
        response = self.session.post(
            f'{self.base_url}/api/v1/optimize-prompt',
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
client = PromptGeneratorClient('http://127.0.0.1:8000')

# Generate prompt
result = client.generate_prompt(
    description='Extract key information from customer support tickets',
    target_llm='claude',
    complexity='complex',
    include_examples=True
)

print(f"Generated prompt: {result['prompt']['task']}")
print(f"Tokens used: {result['metadata']['estimated_tokens']}")

# Check usage
usage = client.get_usage()
print(f"Requests remaining: {usage['daily_limits']['requests']['remaining']}")
```

### cURL Examples

#### Generate Prompt (Anonymous)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a system to categorize customer support tickets by urgency and department",
    "target_llm": "claude",
    "complexity": "moderate",
    "include_examples": true,
    "optimization_goals": ["clarity", "accuracy"]
  }'
```

#### Generate Prompt (Authenticated)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate-prompt" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "description": "Build a comprehensive data analysis pipeline that processes customer feedback, extracts sentiment and themes, generates insights, and creates recommendations for product teams",
    "target_llm": "claude",
    "complexity": "complex",
    "include_examples": true,
    "optimization_goals": ["accuracy", "clarity", "efficiency"]
  }'
```

#### Check Usage
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://127.0.0.1:8000/api/v1/usage"
```

#### Optimize Prompt
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/optimize-prompt" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "prompt": {
      "task": "sentiment_analysis",
      "instructions": {
        "primary_goal": "Analyze the sentiment of customer feedback"
      },
      "input_format": {
        "type": "string",
        "description": "Customer feedback text"
      },
      "output_format": {
        "type": "object",
        "properties": {
          "sentiment": {"type": "string"},
          "score": {"type": "number"}
        }
      }
    },
    "target_model": "claude",
    "optimization_criteria": ["token_efficiency", "clarity"]
  }'
```

---

## Best Practices

### 1. Authentication Strategy
- **Start Anonymous**: Test the API without registration for quick evaluation
- **Register Early**: Register when you hit 50% of anonymous limits for seamless upgrade
- **Token Management**: Store JWT tokens securely and refresh before expiration

### 2. Rate Limit Management
- **Monitor Usage**: Check `/api/v1/usage` endpoint regularly
- **Handle 429 Errors**: Implement retry logic with respect for rate limits
- **Cache Results**: Cache generated prompts to avoid regenerating the same content
- **Complexity Optimization**: Use 'simple' complexity when possible to save tokens

### 3. Prompt Generation
- **Be Specific**: Provide detailed, specific descriptions for better prompt quality
- **Choose Right Complexity**: 
  - Simple: Quick tasks, basic formatting
  - Moderate: Most production use cases
  - Complex: Advanced reasoning, multiple examples
- **Include Examples**: Enable examples for better LLM performance
- **Test First**: Use `/test-prompt` endpoint to validate before production use

### 4. Error Handling
```python
try:
    result = client.generate_prompt(description)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Rate limit exceeded
        retry_after = e.response.headers.get('Retry-After', 60)
        print(f"Rate limited, retry after {retry_after} seconds")
    elif e.response.status_code == 400:
        error_data = e.response.json()
        if error_data.get('error') == 'REQUEST_TOO_LARGE':
            # Request too large, reduce complexity
            print("Request too large, try 'simple' complexity")
    else:
        print(f"API error: {e.response.status_code}")
```

### 5. Token Optimization
- **Estimate First**: Use the API's token estimation in responses to plan usage
- **Optimize Prompts**: Use the `/optimize-prompt` endpoint for token efficiency  
- **Monitor Daily Usage**: Track token consumption to avoid hitting limits
- **Batch Operations**: Group related prompts to minimize overhead

### 6. Production Deployment
- **Environment Variables**: Configure API keys and endpoints via environment variables
- **Health Checks**: Monitor `/health` endpoint for API availability
- **Logging**: Log API responses and rate limit headers for monitoring
- **Graceful Degradation**: Handle API unavailability gracefully in your application

### 7. Security Considerations
- **Secure Token Storage**: Never log or expose JWT tokens
- **Input Validation**: Validate user inputs before sending to the API
- **Rate Limit Respect**: Don't attempt to circumvent rate limiting
- **Error Message Handling**: Don't expose internal API error messages to end users

---

## Interactive Documentation

For interactive API exploration and testing, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

These interfaces allow you to test all endpoints directly in your browser with real API responses.

---

## Support & Community

- **Documentation**: Complete guides and examples in this repository
- **Issues**: Report bugs and request features via GitHub issues  
- **Examples**: See the `/examples` directory for complete integration samples
- **Changelog**: Track all changes and new features in `CHANGELOG.md`

---

*This documentation is automatically updated with each API release. Last updated: 2025-01-10*
