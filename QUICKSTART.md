# 🚀 Quick Start Guide

این راهنمای سریع به شما کمک می‌کند تا پروژه **SEORankPulse** را در کمتر از 5 دقیقه راه‌اندازی کنید.

## پیش‌نیازها

فقط دو چیز نیاز دارید:
- [Docker Desktop](https://www.docker.com/products/docker-desktop) نصب شده باشد
- [Git](https://git-scm.com/) نصب شده باشد

## مراحل راه‌اندازی

### 1. دانلود پروژه

```bash
cd c:/development
git clone <repository-url> seo
cd seo
```

### 2. ایجاد فایل Environment

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

**مهم:** فایل `.env` را باز کنید و حداقل این مقادیر را تنظیم کنید:

```env
# این کلیدها را تغییر دهید (برای development می‌توانید همینها را نگه دارید)
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database passwords
POSTGRES_PASSWORD=seo_password_123
NEO4J_PASSWORD=neo4j_password_123

# اگر می‌خواهید از AI features استفاده کنید، این کلیدها را اضافه کنید:
HUGGINGFACE_API_KEY=your-hf-key-here  # از https://huggingface.co
GOOGLE_CLOUD_API_KEY=your-google-key  # از https://console.cloud.google.com
```

### 3. راه‌اندازی با Docker

```bash
docker-compose up -d
```

این دستور تمام سرویس‌های زیر را راه‌اندازی می‌کند:
- PostgreSQL (Database)
- Redis (Task Queue)
- Neo4j (Graph Database)
- Elasticsearch (Search Engine)
- Backend (FastAPI)
- Celery Worker (Background Tasks)
- Celery Beat (Scheduler)
- Frontend (Next.js)

**منتظر بمانید تا همه سرویس‌ها بالا بیایند** (حدود 1-2 دقیقه اول بار).

### 4. ایجاد Database Tables

```bash
# Windows PowerShell
docker-compose exec backend alembic upgrade head

# Linux/Mac
docker-compose exec backend alembic upgrade head
```

### 5. دسترسی به Application

پروژه آماده است! 🎉

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: `neo4j`, password: `neo4j_password_123`)

## اولین استفاده

### 1. ایجاد حساب کاربری

از طریق API documentation (http://localhost:8000/docs):

1. به بخش **Authentication** بروید
2. `POST /api/v1/auth/register` را باز کنید
3. روی "Try it out" کلیک کنید
4. اطلاعات را وارد کنید:

```json
{
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User"
}
```

5. "Execute" را بزنید

### 2. Login و دریافت Token

1. `POST /api/v1/auth/login` را باز کنید
2. اطلاعات login را وارد کنید:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

3. `access_token` را کپی کنید

### 3. Authorize کردن در Swagger

1. روی دکمه **Authorize** (🔒) بالای صفحه کلیک کنید
2. در قسمت Value بنویسید: `Bearer YOUR_ACCESS_TOKEN`
3. Authorize را بزنید

### 4. ایجاد اولین Project

1. به بخش **Projects** بروید
2. `POST /api/v1/projects` را باز کنید
3. پروژه خود را ایجاد کنید:

```json
{
  "name": "My Website",
  "domain": "example.com",
  "description": "SEO analysis for my website",
  "max_depth": 5,
  "crawl_delay_ms": 1000
}
```

### 5. شروع اولین Crawl

1. `project_id` پروژه ایجاد شده را کپی کنید
2. به بخش **Crawls** بروید
3. `POST /api/v1/crawls` را باز کنید
4. شروع کنید:

```json
{
  "project_id": 1
}
```

### 6. مشاهده Progress

1. `crawl_id` را کپی کنید
2. `GET /api/v1/crawls/{crawl_id}/progress` را استفاده کنید

## دستورات مفید

### چک کردن وضعیت سرویس‌ها

```bash
docker-compose ps
```

### مشاهده Logs

```bash
# همه سرویس‌ها
docker-compose logs -f

# فقط backend
docker-compose logs -f backend

# فقط frontend
docker-compose logs -f frontend

# فقط celery worker
docker-compose logs -f celery_worker
```

### Restart کردن سرویس خاص

```bash
docker-compose restart backend
docker-compose restart frontend
docker-compose restart celery_worker
```

### Stop کردن همه سرویس‌ها

```bash
docker-compose down
```

### Stop و پاک کردن همه data

```bash
docker-compose down -v
```

## عیب‌یابی سریع

### Backend نمی‌تواند به PostgreSQL وصل شود

```bash
# چک کنید PostgreSQL بالا آمده باشد
docker-compose ps postgres

# Restart
docker-compose restart postgres backend
```

### Celery Worker Error

```bash
# چک کنید Redis در حال اجرا باشد
docker-compose ps redis

# Restart worker
docker-compose restart celery_worker
```

### Frontend به Backend متصل نمیشود

```bash
# مطمئن شوید NEXT_PUBLIC_API_URL در .env درست است
# باید http://localhost:8000 باشد

# Restart frontend
docker-compose restart frontend
```

### Port در حال استفاده است

اگر خطای "port already in use" دریافت کردید:

```bash
# چک کنید چه برنامه‌ای port را استفاده می‌کند
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :8000
lsof -i :3000

# سپس process را kill کنید یا port را در docker-compose.yml تغییر دهید
```

## مراحل بعدی

✅ پروژه شما راه‌اندازی شد!

**حالا می‌توانید:**

1. **Frontend را توسعه دهید:**
   - صفحات Login/Register بسازید
   - Dashboard layout طراحی کنید
   - نمودارها و charts اضافه کنید

2. **Backend را کامل کنید:**
   - Neo4j integration برای link graph
   - AI services integration
   - Playwright برای JS rendering

3. **Feature‌های جدید اضافه کنید:**
   - Report generation (PDF/Excel)
   - Email notifications
   - Scheduled crawls
   - Webhook support

## مستندات بیشتر

- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - خلاصه کامل پیاده‌سازی
- [README.md](./README.md) - مستندات کامل پروژه
- API Docs: http://localhost:8000/docs

## پشتیبانی

اگر مشکلی پیش آمد:

1. Logs را چک کنید: `docker-compose logs -f`
2. مطمئن شوید تمام سرویس‌ها healthy هستند: `docker-compose ps`
3. مستندات را بخوانید
4. Issue ایجاد کنید در GitHub

---

**نکته:** این یک MVP است. برخی فیچرها (مثل AI analysis) هنوز کامل نشده‌اند اما structure آماده است.

Happy coding! 🚀
