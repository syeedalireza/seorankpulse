# 🚀 راه‌اندازی سریع بدون Build طولانی

## ✅ Databases بالا آمدند!

همه چیز آماده است:
- ✅ PostgreSQL: localhost:5432
- ✅ Redis: localhost:6379
- ✅ Neo4j: localhost:7474
- ✅ Elasticsearch: localhost:9200

## 🎯 راه‌اندازی Backend و Frontend

### گام 1: راه‌اندازی Backend

```powershell
# Terminal 1 - Backend
cd C:\development\seo\backend

# ایجاد virtual environment
python -m venv venv

# فعال کردن
.\venv\Scripts\activate

# نصب dependencies
pip install -r requirements.txt

# اجرای migrations
$env:DATABASE_URL="postgresql+asyncpg://seo_user:seo_password@localhost:5432/seo_db"
$env:SECRET_KEY="dev-secret-key-12345"
$env:JWT_SECRET_KEY="dev-jwt-secret-key-12345"
$env:POSTGRES_PASSWORD="seo_password"
$env:NEO4J_PASSWORD="neo4j_password"

alembic upgrade head

# اجرای server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### گام 2: راه‌اندازی Frontend

```powershell
# Terminal 2 - Frontend  
cd C:\development\seo\frontend

# نصب dependencies
npm install

# اجرای dev server
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev
```

### گام 3: دسترسی

**Frontend Dashboard:**
http://localhost:3000

**Backend API:**
http://localhost:8000

**API Docs:**
http://localhost:8000/docs

---

## یا استفاده از Script خودکار:

فایل `start.ps1` را اجرا کنید:

```powershell
.\start.ps1
```

این script همه کارها را خودکار انجام می‌دهد.

---

**پروژه شما آماده است!** 🎊
