# 🔧 راهنمای عیب‌یابی

## مشکلات رایج و راه‌حل‌ها

### 1. Docker Build ناموفق است

#### علائم:
```
Error: failed to solve: process ... did not complete successfully
```

#### راه‌حل:
```powershell
# پاک کردن cache و build مجدد
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### 2. Network Timeout هنگام Pull

#### علائم:
```
net/http: TLS handshake timeout
```

#### راه‌حل:
```powershell
# تلاش مجدد با timeout بیشتر
$env:COMPOSE_HTTP_TIMEOUT="200"
docker-compose pull

# یا pull تک‌تک
docker pull postgres:16-alpine
docker pull redis:7-alpine  
docker pull neo4j:5-community
docker pull elasticsearch:8.12.0
```

### 3. Port در حال استفاده است

#### علائم:
```
Bind for 0.0.0.0:80 failed: port is already allocated
```

#### راه‌حل:
```powershell
# یافتن process
netstat -ano | findstr :80

# Kill process (PID را جایگزین کنید)
taskkill /PID <PID> /F

# یا port را تغییر دهید
# در docker-compose.yml:
# ports: - "8080:80"
```

### 4. Backend به PostgreSQL متصل نمیشود

#### راه‌حل:
```powershell
# چک کنید PostgreSQL healthy است
docker-compose ps postgres

# اگر unhealthy است:
docker-compose logs postgres

# Restart
docker-compose restart postgres
sleep 10
docker-compose restart backend
```

### 5. Frontend npm install خطا می‌دهد

#### راه‌حل:
```powershell
# پاک کردن node_modules
Remove-Item -Recurse -Force frontend\node_modules

# Build بدون cache
docker-compose build --no-cache frontend
```

### 6. دسترسی Denied هنگام اجرای Alembic

#### راه‌حل:
```powershell
# مطمئن شوید backend container در حال اجرا است
docker-compose ps backend

# اگر نیست، logs را چک کنید
docker-compose logs backend

# سپس دوباره تلاش کنید
docker-compose exec backend alembic upgrade head
```

### 7. Celery Worker شروع نمیشود

#### راه‌حل:
```powershell
# چک کنید Redis در حال اجرا است
docker-compose ps redis

# مشاهده logs
docker-compose logs celery_worker

# Restart
docker-compose restart redis celery_worker
```

### 8. Frontend صفحه سفید نشان می‌دهد

#### راه‌حل:
```powershell
# چک browser console برای errors

# مطمئن شوید API_URL درست است
# در .env:
# NEXT_PUBLIC_API_URL=http://localhost/api

# Rebuild frontend
docker-compose up -d --build frontend
```

## راه‌حل‌های کلی

### Reset کامل

اگر همه چیز خراب شد:

```powershell
# توقف همه
docker-compose down -v

# پاک کردن همه Docker data
docker system prune -a --volumes

# شروع مجدد
docker-compose up -d --build
```

### Build تدریجی

به جای build همه با هم:

```powershell
# فقط databases را بالا بیاورید
docker-compose up -d postgres redis neo4j elasticsearch

# صبر کنید تا healthy شوند
docker-compose ps

# سپس backend
docker-compose up -d --build backend celery_worker celery_beat

# بعد frontend
docker-compose up -d --build frontend

# در نهایت nginx
docker-compose up -d --build nginx
```

### راه‌اندازی بدون Docker

اگر Docker مشکل دارد:

```powershell
# PostgreSQL را manually نصب کنید
# Redis را manually نصب کنید

cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# تنظیم .env با localhost addresses
# DATABASE_URL=postgresql+asyncpg://seo_user:password@localhost:5432/seo_db

alembic upgrade head
uvicorn app.main:app --reload

# Terminal دیگر
cd frontend
npm install
npm run dev
```

## چک‌لیست عیب‌یابی

- [ ] Docker Desktop در حال اجرا است؟
- [ ] اتصال اینترنت فعال است؟
- [ ] Port 80 آزاد است؟ (netstat -ano | findstr :80)
- [ ] فایل `.env` وجود دارد؟
- [ ] Docker has enough resources (4GB+ RAM)?
- [ ] Antivirus Docker را block نمی‌کند؟
- [ ] Windows Firewall اجازه می‌دهد؟

## لاگ‌های مفید

```powershell
# همه logs
docker-compose logs

# فقط errors
docker-compose logs | Select-String "error" -Context 3

# مشاهده realtime
docker-compose logs -f backend

# آخرین 100 خط
docker-compose logs --tail=100 backend
```

## کمک بیشتر

اگر مشکل حل نشد:

1. مستندات Docker Desktop: https://docs.docker.com/desktop/
2. FastAPI Docs: https://fastapi.tiangolo.com/
3. Next.js Docs: https://nextjs.org/docs

یا Issue در GitHub ایجاد کنید.
