# AI JSON Prompt Generator API

A comprehensive FastAPI application that generates structured JSON prompts for Large Language Models (LLMs) from natural language descriptions. This API provides intelligent prompt engineering capabilities with support for multiple LLM providers, optimization algorithms, and advanced prompt components.

## 🚀 Features

### Core Functionality
- **🧠 Natural Language Processing**: Convert natural language descriptions into structured JSON prompts
- **🤖 Multi-LLM Support**: Compatible with Claude, GPT-4, Gemini, and Llama models
- **🔧 Prompt Optimization**: Intelligent optimization for token efficiency and clarity
- **🔄 Format Conversion**: Convert prompts between different LLM formats
- **🧪 Prompt Testing**: Built-in testing capabilities with sample inputs
- **🔀 Prompt Merging**: Combine multiple prompts with different strategies
- **📊 Quality Analysis**: Comprehensive prompt quality assessment and scoring
- **📝 Template Management**: Pre-built and customizable prompt templates

### User Experience & Security
- **🔐 JWT Authentication**: Secure API access with user management
- **👤 Anonymous Access**: Use the API without registration (with daily limits)
- **📈 Usage Monitoring**: Real-time tracking of requests and token usage
- **⚡ Rate Limiting**: Smart daily limits with upgrade incentives
- **🛡️ IP-Based Tracking**: Fair usage enforcement for anonymous users

### Technical Features
- **💾 Database Persistence**: SQLite/PostgreSQL support for prompt storage
- **⚡ Redis Caching**: High-performance rate limiting and caching
- **📖 API Documentation**: Interactive OpenAPI/Swagger documentation
- **🔄 Async Processing**: Full async/await implementation for optimal performance
- **🐳 Production Ready**: Comprehensive error handling and monitoring

## 📁 Project Structure

```
ai-json-prompt-generator/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── models/
│   │   └── database.py      # SQLAlchemy models
│   ├── api/
│   │   ├── dependencies.py  # JWT auth and shared dependencies
│   │   └── routes/
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── generate.py  # Prompt generation endpoints
│   │       ├── optimize.py  # Prompt optimization endpoints
│   │       ├── convert.py   # Format conversion endpoints
│   │       ├── templates.py # Template management endpoints
│   │       ├── test.py      # Prompt testing endpoints
│   │       ├── analyze.py   # Prompt analysis endpoints
│   │       └── merge.py     # Prompt merging endpoints
│   ├── services/
│   │   ├── llm_service.py   # LLM integration layer
│   │   └── prompt_generator.py # Core prompt generation logic
│   ├── utils/
│   │   └── token_counter.py # Token estimation utilities
│   └── schemas/
│       ├── request_schemas.py  # API request models
│       ├── response_schemas.py # API response models
│       └── prompt_schemas.py   # JSON prompt structure schemas
├── templates/
│   └── base_templates.json # Pre-built prompt templates
├── tests/
│   └── test_api.py        # API tests
├── scripts/
│   ├── dev.ps1           # Development server script
│   ├── test.ps1          # Test runner script
│   └── install.ps1       # Dependency installer
├── docs/                 # Documentation
├── venv/                 # Virtual environment
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
├── app-req.json        # Application requirements specification
└── README.md           # This file
```

## Setup

### Prerequisites

- Python 3.8+
- PowerShell (Windows)

### Installation

1. **Clone or navigate to the project directory:**
   ```powershell
   cd C:\projects\json2prompt
   ```

2. **Run the installation script:**
   ```powershell
   .\scripts\install.ps1
   ```

   Or manually:
   ```powershell
   # Activate virtual environment
   .\venv\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

### Configuration

Edit the `.env` file to customize application settings:

```env
# Application Configuration
APP_NAME=JSON2Prompt API
DEBUG=true
HOST=127.0.0.1
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# API Configuration
SECRET_KEY=your-secret-key-change-this-in-production
```

## Usage

### Starting the Development Server

```powershell
.\scripts\dev.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at:
- **Application**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc

### 🔗 API Endpoints

#### 🔐 Authentication (Optional)
- `POST /auth/register` - Register a new user for enhanced limits
- `POST /auth/login` - Authenticate and get JWT token
- `GET /auth/me` - Get current user information
- `POST /auth/refresh` - Refresh JWT token

> **Note**: Authentication is optional! Anonymous users can use the API with daily limits.

#### 🧠 Core Prompt Generation
- `POST /api/v1/generate-prompt` - **Generate structured prompts from natural language**
  - Supports both anonymous and registered users
  - Anonymous: 10 requests/day, 50K tokens/day
  - Registered: 50 requests/day, 200K tokens/day
- `POST /api/v1/optimize-prompt` - **Optimize existing prompts for better performance**
  - Token efficiency and clarity improvements
  - Anonymous: 5 requests/day, Registered: 20 requests/day
- `POST /api/v1/convert-prompt` - **Convert prompts between LLM formats**
  - OpenAI ↔ Anthropic ↔ Generic formats
- `POST /api/v1/test-prompt` - **Test prompts with sample inputs**
  - Validate prompt effectiveness before deployment
  - Anonymous: 5 requests/day, Registered: 20 requests/day
- `POST /api/v1/analyze-prompt` - **Analyze prompt quality and effectiveness**
  - Quality scoring and improvement suggestions
- `POST /api/v1/merge-prompts` - **Combine multiple prompts intelligently**
  - Sequential, parallel, or conditional merging strategies

#### 📝 Template Management
- `GET /api/v1/templates` - **List available prompt templates**
  - Filter by category and complexity
  - Unlimited access for all users
- `GET /api/v1/templates/{template_id}` - **Get specific template details**
  - Pre-built templates for common use cases

#### 📈 Usage Monitoring
- `GET /api/v1/usage` - **Comprehensive usage statistics**
  - Daily request and token usage with limits
  - Upgrade benefits for anonymous users
- `GET /api/v1/usage/simple` - **Simple usage data for frontend components**
  - Essential usage information with warning levels

#### ❤️ Health & Status
- `GET /health` - **Basic health check**
- `GET /` - **API information and available endpoints**
  - Welcome message with endpoint overview

## 🚀 **API Usage Examples**

### Anonymous User Usage (No Authentication)

#### Generate a Simple Prompt
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Analyze customer support tickets to categorize them by urgency and sentiment",
    "target_llm": "claude",
    "complexity": "simple",
    "include_examples": true
  }'
```

#### Check Usage Statistics
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/usage"
```

#### Response with Rate Limiting Info
```json
{
  "prompt": {
    "task": "analysis",
    "system_message": "You are a skilled analyst capable of extracting insights from complex information.",
    "instructions": {
      "primary_goal": "Analyze customer support tickets to categorize them by urgency and sentiment",
      "steps": [
        "Carefully read and understand the input",
        "Process the input according to the task requirements",
        "Generate the output in the specified format"
      ]
    },
    "input_format": {
      "type": "string",
      "description": "Input text to process",
      "constraints": []
    },
    "output_format": {
      "type": "object",
      "description": "Structured output based on task requirements"
    },
    "examples": [],
    "constraints": [],
    "edge_cases": [],
    "metadata": {
      "version": "1.0",
      "estimated_tokens": 245,
      "target_models": ["claude"]
    }
  },
  "metadata": {
    "estimated_tokens": 245,
    "complexity_score": 0.5,
    "suggestions": [
      "Consider adding examples to improve clarity and accuracy"
    ],
    "version": "1.0"
  },
  "rate_limit_info": {
    "requests_remaining": 9,
    "tokens_remaining": 47755,
    "user_type": "anonymous"
  }
}
```

### Registered User Usage (With JWT Authentication)

#### 1. Register a New User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "developer123",
    "email": "dev@example.com",
    "password": "securePassword123"
  }'
```

#### 2. Login and Get JWT Token
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

#### 3. Generate Complex Prompt (Registered Users Only)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate-prompt" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Create a comprehensive data analysis system that processes customer feedback, extracts sentiment, identifies key themes, and generates actionable insights with confidence scores and recommendations for product teams",
    "target_llm": "claude",
    "complexity": "complex",
    "include_examples": true,
    "optimization_goals": ["clarity", "accuracy", "efficiency"]
  }'
```

#### 4. Optimize an Existing Prompt
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/optimize-prompt" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "task": "analysis",
      "instructions": {
        "primary_goal": "Analyze text for sentiment"
      }
    },
    "target_model": "claude",
    "optimization_criteria": ["token_efficiency", "clarity"]
  }'
```

#### 5. Test a Prompt
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/test-prompt" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": {
      "task": "sentiment_analysis",
      "instructions": {
        "primary_goal": "Analyze sentiment of customer feedback"
      }
    },
    "test_input": "I love this product! It exceeded my expectations.",
    "target_model": "claude"
  }'
```

## ⚡ **Rate Limiting & Usage Tiers**

### User Tiers

| Feature | Anonymous Users | Registered Users |
|---------|----------------|------------------|
| **Daily Requests** | 10 | 50 |
| **Daily Tokens** | 50,000 | 200,000 |
| **Max Tokens/Request** | 5,000 | 10,000 |
| **Complex Prompts** | ❌ | ✅ |
| **Prompt History** | ❌ | ✅ |
| **Priority Support** | ❌ | ✅ |

### Rate Limit Headers

All responses include rate limiting information:

```http
X-RateLimit-Type: daily
X-RateLimit-Limit-Requests: 10
X-RateLimit-Remaining-Requests: 7
X-RateLimit-Limit-Tokens: 50000
X-RateLimit-Remaining-Tokens: 42000
X-RateLimit-Reset: 2025-01-11T00:00:00Z
X-RateLimit-User-Type: anonymous
```

### Error Responses

#### Rate Limit Exceeded (429)
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

### Prompt Complexity Levels

1. **Simple**: Basic prompts with minimal structure (~1,500 tokens)
   - Quick task definitions
   - Basic input/output specifications
   - Suitable for straightforward use cases

2. **Moderate**: Well-structured prompts with examples (~3,000 tokens)
   - Detailed instructions and context
   - Example inputs and outputs
   - Better accuracy and consistency

3. **Complex**: Comprehensive prompts with advanced features (~5,000+ tokens)
   - Chain-of-thought reasoning
   - Multiple examples and edge cases
   - Advanced validation and constraints
   - **Available only to registered users**

### Running Tests

```powershell
.\scripts\test.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

## Development

### Adding New Features

1. Create new routes in `app/routes/`
2. Add configuration options to `app/config.py`
3. Update environment variables in `.env`
4. Write tests in `tests/`

### Code Quality

The project uses:
- **FastAPI** for the web framework
- **Pydantic** for data validation
- **Uvicorn** for ASGI server
- **Pytest** for testing

### Environment Variables

All configuration is handled through environment variables defined in `.env`. Never hardcode sensitive values in the code.

## Deployment

For production deployment:

1. Set `DEBUG=false` in environment variables
2. Generate a secure `SECRET_KEY`
3. Configure appropriate `ALLOWED_ORIGINS`
4. Use a production ASGI server like Gunicorn with Uvicorn workers
5. Set up proper logging and monitoring

## License

This project is licensed under the MIT License.
