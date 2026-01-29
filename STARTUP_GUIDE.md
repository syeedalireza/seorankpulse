# Startup Guide - Get Your SEO Platform Running

## راهنمای راه‌اندازی سریع

این راهنما به شما کمک می‌کند پلتفرم SEO را در عرض 5 دقیقه راه‌اندازی کنید.

---

## گام 1: پیش‌نیازها

✅ Docker Desktop نصب باشد
✅ Git نصب باشد
✅ 8GB RAM آزاد (توصیه می‌شود)
✅ 10GB فضای دیسک

---

## گام 2: کانفیگ Environment Variables

```powershell
# کپی کردن فایل نمونه
cp .env.example .env

# ویرایش .env
notepad .env
```

### حداقل تنظیمات مورد نیاز:

```bash
# Database (می‌توانید همان‌ها را نگه دارید)
POSTGRES_PASSWORD=seo_password
NEO4J_PASSWORD=neo4j_password

# JWT Secret (تغییر دهید!)
JWT_SECRET_KEY=your-very-secret-key-here-change-this

# AI Features (اختیاری - برای فیچرهای AI)
OPENAI_API_KEY=sk-...  # از platform.openai.com

# SERP Tracking (اختیاری)
SERP_API_KEY=...  # از serpapi.com
```

---

## گام 3: راه‌اندازی با Docker

```powershell
# شروع تمام سرویس‌ها
docker-compose up -d

# مشاهده logs (برای بررسی که همه چیز OK است)
docker-compose logs -f
```

**صبر کنید تا همه سرویس‌ها healthy شوند (حدود 2-3 دقیقه)**

---

## گام 4: اجرای Database Migrations

```powershell
# اجرای migrationها
docker-compose exec backend alembic upgrade head

# اگر نیاز به migration جدید دارید:
docker-compose exec backend alembic revision --autogenerate -m "Add new models"
```

---

## گام 5: نصب Playwright Browsers

```powershell
# نصب Chromium برای JavaScript rendering
docker-compose exec backend playwright install chromium
```

---

## گام 6: دسترسی به Platform

🌐 **Frontend Dashboard:** http://localhost
📚 **API Documentation:** http://localhost/docs
🌸 **Flower (Celery Monitor):** http://localhost:5555
🔍 **Neo4j Browser:** http://localhost:7474

---

## گام 7: اولین پروژه را بسازید

1. **رفتن به:** http://localhost
2. **ثبت‌نام:** ایجاد اکانت جدید
3. **ورود:** با email و password
4. **Create Project:** یک پروژه SEO جدید بسازید
5. **Start Crawl:** اولین crawl را شروع کنید

---

## ✨ امکانات در دسترس

### بدون API Key:
- ✅ Web Crawling (با یا بدون JavaScript)
- ✅ Technical SEO Analysis
- ✅ Link Graph Analysis (PageRank)
- ✅ Duplicate Content Detection
- ✅ Image Analysis
- ✅ Accessibility Audits
- ✅ Redirect Chain Analysis
- ✅ Excel Export
- ✅ Sitemap Generation
- ✅ Log File Analysis
- ✅ Team Collaboration
- ✅ Custom Dashboards
- ✅ Historical Tracking

### با OpenAI API Key:
- ✨ AI Content Quality Scoring
- ✨ AI Alt Text Generation
- ✨ Content Brief Generation
- ✨ Competitor Content Comparison

### با SerpAPI Key:
- 📈 Keyword Ranking Tracking
- 📈 SERP Position Monitoring
- 📈 Competitor Ranking Analysis

### با Google Search Console:
- 🔍 URL Inspection
- 🔍 Search Analytics
- 🔍 Indexing Status

---

## 🔧 Troubleshooting

### مشکل: Docker services شروع نمی‌شوند
```powershell
# چک کردن وضعیت
docker-compose ps

# restart کردن سرویس‌های مشکل‌دار
docker-compose restart backend celery_worker

# مشاهده logs برای دیدن خطا
docker-compose logs backend
```

### مشکل: Database connection error
```powershell
# چک کردن که PostgreSQL ready است
docker-compose exec postgres pg_isready

# اگر نیاز به reset دارید:
docker-compose down -v
docker-compose up -d
```

### مشکل: Frontend نمایش داده نمی‌شود
```powershell
# restart کردن Nginx
docker-compose restart nginx

# چک کردن logs
docker-compose logs nginx frontend
```

### مشکل: Playwright خطا می‌دهد
```powershell
# نصب browsers
docker-compose exec backend playwright install chromium

# اگر بازهم مشکل دارد، JS rendering را disable کنید
# enable_js: false
```

---

## 📱 دسترسی به Feature های جدید

### SERP Tracking
→ http://localhost/serp-tracking

### Competitive Analysis
→ http://localhost/competitors

### Team Collaboration
→ http://localhost/team

### Alerts & Monitoring
→ http://localhost/alerts

### Custom Dashboards
→ http://localhost/dashboards

### Lighthouse Analysis
→ http://localhost/analysis/lighthouse

### Accessibility Audit
→ http://localhost/analysis/accessibility

### Duplicate Content
→ http://localhost/analysis/duplicates

---

## 🎯 Quick Wins

### 1. اولین Crawl با JavaScript
```
1. Create Project
2. Enable "JavaScript Rendering"
3. Start Crawl
4. View results with JS-rendered content
```

### 2. تست یک URL سریع (List Mode)
```
1. Go to Project
2. Upload URL list (CSV/TXT)
3. Get instant analysis without full crawl
```

### 3. Track Keyword Rankings
```
1. Go to SERP Tracking page
2. Add keywords
3. Click "Check Rankings"
4. See your positions in Google
```

### 4. Get AI Content Recommendations
```
1. Select a page
2. Click "AI Analysis"
3. Get AI-powered improvement suggestions
```

### 5. Setup Monitoring
```
1. Go to Alerts page
2. Click "Start Monitoring"
3. Choose frequency (daily/weekly)
4. Get automatic alerts for issues
```

---

## 📞 Support

### Documentation
- `README.md` - Project overview
- `docs/FEATURES_GUIDE.md` - Detailed feature guide
- `docs/API_DOCUMENTATION.md` - Complete API reference
- `docs/QUICK_REFERENCE.md` - Quick reference

### Interactive Docs
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

### Monitoring
- Flower (Celery): http://localhost:5555
- Neo4j Browser: http://localhost:7474

---

## 🚀 Production Deployment

برای استقرار در production:

1. تغییر `ENVIRONMENT=production` در .env
2. تنظیم `SECRET_KEY` و `JWT_SECRET_KEY` با مقادیر امن
3. تنظیم `CORS_ORIGINS` به domain واقعی
4. استفاده از SSL/TLS (Nginx با Let's Encrypt)
5. تنظیم backup برای دیتابیس‌ها
6. نظارت بر logs و metrics

---

## ✅ Checklist راه‌اندازی

- [ ] Docker Desktop اجرا شده
- [ ] فایل .env کانفیگ شده
- [ ] `docker-compose up -d` اجرا شده
- [ ] همه سرویس‌ها healthy هستند
- [ ] Migrations اجرا شده
- [ ] Playwright browsers نصب شده
- [ ] Frontend در http://localhost باز می‌شود
- [ ] API docs در http://localhost/docs کار می‌کند
- [ ] اکانت کاربری ساخته شده
- [ ] اولین پروژه ساخته شده
- [ ] اولین crawl با موفقیت اجرا شده

---

**اگر همه checklist ها ✅ باشند، پلتفرم شما آماده است!** 🎊

**موفق باشید!** 🚀
