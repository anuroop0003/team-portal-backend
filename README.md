# Team Portal Backend

## Quick Start

1. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   - Create `.env` file based on existing environment settings.

3. **Database Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Run Application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Documentation
- **Swagger:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
