# راه‌اندازی Manual (بدون مشکلات Docker Build)

## ✅ وضعیت فعلی:

**Databases بالا آمدند:**
- ✅ PostgreSQL: localhost:5432
- ✅ Redis: localhost:6379  
- ✅ Neo4j: localhost:7474
- ✅ Elasticsearch: localhost:9200

## 🚀 راه‌اندازی Backend

**Terminal 1 - Backend:**

```powershell
cd C:\development\seo\backend

# Virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install
pip install fastapi uvicorn[standard] sqlalchemy[asyncio] alembic asyncpg python-jose[cryptography] passlib[bcrypt] python-dotenv pydantic-settings httpx beautifulsoup4 lxml neo4j redis celery

# Environment
$env:DATABASE_URL="postgresql+asyncpg://seo_user:seo_password@localhost:5432/seo_db"
$env:SECRET_KEY="dev-secret-key"
$env:JWT_SECRET_KEY="dev-jwt-key"
$env:POSTGRES_PASSWORD="seo_password"
$env:NEO4J_PASSWORD="neo4j_password"

# Migration
alembic upgrade head

# Run
uvicorn app.main:app --reload
```

## 🎨 راه‌اندازی Frontend

**Terminal 2 - Frontend:**

```powershell
cd C:\development\seo\frontend

# Install
npm install

# Run
npm run dev
```

## ✅ دسترسی

- Frontend: http://localhost:3000
- Backend: http://localhost:8000  
- API Docs: http://localhost:8000/docs

---

**همین! پروژه شما آماده است!** 🎉
