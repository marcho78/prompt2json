#!/usr/bin/env python3
"""
Deployment readiness checker for JSON2Prompt API
Tests essential configurations before deployment
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check required environment variables"""
    required_vars = [
        'DATABASE_URL'
    ]
    
    optional_vars = [
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY'
    ]
    
    issues = []
    
    # Check required variables
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"❌ Missing required environment variable: {var}")
    
    # Check optional variables (at least one LLM key should be present)
    llm_keys = [var for var in optional_vars if os.getenv(var)]
    if not llm_keys:
        issues.append("⚠️  No LLM API keys found. At least one is required (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
    else:
        logger.info(f"✅ Found LLM API keys: {', '.join(llm_keys)}")
    
    # Check DATABASE_URL format
    db_url = os.getenv('DATABASE_URL', '')
    if db_url and not db_url.startswith('postgresql://'):
        issues.append(f"❌ DATABASE_URL must start with 'postgresql://'. Got: {db_url[:50]}...")
    elif db_url:
        logger.info("✅ DATABASE_URL format is correct")
    
    return len(issues) == 0, issues

def check_database_connection():
    """Test database connection"""
    try:
        from src.config import settings
        
        # Test database URL generation
        db_url = settings.get_database_url()
        logger.info("✅ Database URL configuration is valid")
        
        # Test database connection (without creating tables)
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True, []
        
    except Exception as e:
        return False, [f"❌ Database connection failed: {str(e)}"]

def check_imports():
    """Test critical imports"""
    issues = []
    
    try:
        from src.config import settings
        logger.info("✅ Configuration import successful")
    except ImportError as e:
        issues.append(f"❌ Config import failed: {e}")
    
    try:
        from src.models.database import User, GeneratedPrompt
        logger.info("✅ Database models import successful")
    except ImportError as e:
        issues.append(f"❌ Database models import failed: {e}")
    
    try:
        from src.middleware.rate_limiter import rate_limiter
        logger.info("✅ Rate limiter import successful")
    except ImportError as e:
        issues.append(f"❌ Rate limiter import failed: {e}")
    
    try:
        from src.services.llm_service import LLMOrchestrator
        orchestrator = LLMOrchestrator()
        available_providers = orchestrator.get_available_providers()
        if available_providers:
            logger.info(f"✅ LLM services available: {', '.join(available_providers)}")
        else:
            issues.append("❌ No LLM providers available - check API keys")
    except ImportError as e:
        issues.append(f"❌ LLM service import failed: {e}")
    except Exception as e:
        issues.append(f"❌ LLM service initialization failed: {e}")
    
    return len(issues) == 0, issues

def check_critical_routes():
    """Test critical route imports"""
    issues = []
    
    try:
        from src.api.routes import generate, auth, usage
        logger.info("✅ Critical routes import successful")
    except ImportError as e:
        issues.append(f"❌ Routes import failed: {e}")
    
    return len(issues) == 0, issues

async def run_deployment_checks():
    """Run all deployment checks"""
    logger.info("🚀 Starting deployment readiness check...\n")
    
    all_passed = True
    
    # Check 1: Environment Variables
    logger.info("1️⃣ Checking environment variables...")
    env_ok, env_issues = check_environment_variables()
    if not env_ok:
        all_passed = False
        for issue in env_issues:
            logger.error(issue)
    else:
        logger.info("✅ Environment variables OK\n")
    
    # Check 2: Imports
    logger.info("2️⃣ Checking imports...")
    imports_ok, import_issues = check_imports()
    if not imports_ok:
        all_passed = False
        for issue in import_issues:
            logger.error(issue)
    else:
        logger.info("✅ Imports OK\n")
    
    # Check 3: Routes
    logger.info("3️⃣ Checking routes...")
    routes_ok, route_issues = check_critical_routes()
    if not routes_ok:
        all_passed = False
        for issue in route_issues:
            logger.error(issue)
    else:
        logger.info("✅ Routes OK\n")
    
    # Check 4: Database (only if environment is OK)
    if env_ok:
        logger.info("4️⃣ Checking database connection...")
        db_ok, db_issues = check_database_connection()
        if not db_ok:
            all_passed = False
            for issue in db_issues:
                logger.error(issue)
        else:
            logger.info("✅ Database connection OK\n")
    else:
        logger.warning("⏭️  Skipping database check due to environment issues\n")
    
    # Summary
    if all_passed:
        logger.info("🎉 All deployment checks passed! Ready to deploy.")
        return 0
    else:
        logger.error("💥 Some deployment checks failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_deployment_checks())
    sys.exit(exit_code)
