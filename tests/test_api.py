import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_readiness_check():
    """Test readiness check endpoint"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data


def test_json_to_prompt_simple():
    """Test JSON to prompt conversion with simple format"""
    test_data = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }
    
    response = client.post(
        "/api/v1/json-to-prompt",
        json={
            "data": test_data,
            "format_type": "simple"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "metadata" in data
    assert data["metadata"]["format_type"] == "simple"


def test_json_to_prompt_structured():
    """Test JSON to prompt conversion with structured format"""
    test_data = {
        "user": {
            "name": "Jane Smith",
            "details": {
                "age": 25,
                "location": "California"
            }
        }
    }
    
    response = client.post(
        "/api/v1/json-to-prompt",
        json={
            "data": test_data,
            "format_type": "structured"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "=== Data Structure ===" in data["prompt"]


def test_get_templates():
    """Test getting available templates"""
    response = client.get("/api/v1/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) >= 3


def test_invalid_json():
    """Test handling of invalid requests"""
    response = client.post(
        "/api/v1/json-to-prompt",
        json={
            "invalid": "request"
        }
    )
    
    assert response.status_code == 422  # Validation error
