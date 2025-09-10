# GitHub Codespaces Setup - Personal Development Notes

## Quick Start

1. **Create Codespace:**
   - Click "Code" → "Codespaces" → "Create codespace on main"
   - Environment automatically sets up with Python 3.11, Redis, dependencies

2. **Start API:**
   ```bash
   # Quick start with defaults
   bash .devcontainer/start.sh
   
   # Or manual setup
   cp .devcontainer/.env.codespaces .env
   code .env  # Edit configuration
   python main.py
   ```

3. **Access:**
   - API: Codespaces provides the HTTPS URL automatically
   - Docs: `{CODESPACE_URL}/docs`
   - Thunder Client extension included for API testing

## Configuration

- **Environment**: `.devcontainer/.env.codespaces` → `.env`
- **Database**: SQLite in `./data/app.db` (automatically created)
- **Redis**: Auto-starts on localhost:6379
- **Ports**: 8000 (API), 6379 (Redis) - automatically forwarded

## Security Notes

- All sensitive config uses environment variables
- `.env` file excluded from git
- Default SECRET_KEY should be changed for any real testing
- API keys for LLMs can be added to `.env` if needed

## Extensions Included

- Python language support
- Black formatter + Pylint
- Thunder Client for API testing
- JSON/YAML editing support

## Database

- SQLite for development (no external dependencies)
- Tables created automatically on first run
- Located in `./data/app.db`

## Redis

- Auto-starts via postStartCommand
- Used for rate limiting
- localhost:6379, database 0
