# Quick Reference - Key Features

## Essential Commands

### Start Platform
```bash
docker-compose up -d
```

### Run Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Create New Migration
```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Run Tests
```bash
docker-compose exec backend pytest
```

---

## Feature Matrix

| Feature | Status | API Endpoint | Frontend Page |
|---------|--------|--------------|---------------|
| JavaScript Rendering | ✅ | `/projects/{id}/crawl` | Dashboard |
| Lighthouse/Core Web Vitals | ✅ | `/analysis/lighthouse` | `/analysis/lighthouse` |
| List Mode Crawling | ✅ | `/projects/{id}/list-crawl/upload` | Dashboard |
| XML Sitemap Generator | ✅ | `/projects/{id}/export/sitemap` | Export dialog |
| Google Search Console | ✅ | Integrated | Dashboard |
| Excel Export (Multi-sheet) | ✅ | `/projects/{id}/export/excel` | Export dialog |
| Log File Analysis | ✅ | `/logs/upload` | Logs page |
| Duplicate Content | ✅ | `/analysis/duplicates` | `/analysis/duplicates` |
| Image Analysis | ✅ | `/analysis/images` | Analysis page |
| Accessibility Audits | ✅ | `/analysis/accessibility` | `/analysis/accessibility` |
| Redirect Chains | ✅ | `/analysis/redirect-chains` | Analysis page |
| Historical Tracking | ✅ | `/monitoring/` | Dashboard |
| AI Content Scoring | ✅ | `/ai/content-score` | AI Tools |
| AI Alt Text | ✅ | `/ai/alt-text/generate` | AI Tools |
| Continuous Monitoring | ✅ | `/projects/{id}/monitoring/start` | `/alerts` |
| Competitive Analysis | ✅ | `/projects/{id}/competitors/compare` | `/competitors` |
| SERP Tracking | ✅ | `/keywords/check` | `/serp-tracking` |
| Team Collaboration | ✅ | `/projects/{id}/team/` | `/team` |
| Custom Dashboards | ✅ | `/dashboards` | `/dashboards` |

---

## API Quick Reference

### Authentication
```bash
# Login
POST /api/v1/auth/login
Body: { "username": "email@example.com", "password": "password" }

# Register
POST /api/v1/auth/register
Body: { "email": "...", "password": "...", "full_name": "..." }
```

### Start Crawl
```bash
POST /api/v1/projects/{id}/crawl
Headers: Authorization: Bearer <token>
Body: { "enable_js": true }
```

### Check Rankings
```bash
POST /api/v1/keywords/check
Body: {
  "keywords": ["keyword1", "keyword2"],
  "location": "United States",
  "project_id": 1
}
```

### Generate Alt Text
```bash
POST /api/v1/ai/alt-text/generate
Body: {
  "image_url": "https://...",
  "max_length": 125
}
```

### Export to Excel
```bash
GET /api/v1/projects/{id}/export/excel
```

---

## Service Ports

- **Frontend:** http://localhost (via Nginx)
- **Backend API:** http://localhost/api
- **API Docs:** http://localhost/docs
- **Flower (Celery):** http://localhost:5555
- **Neo4j Browser:** http://localhost:7474
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379
- **Elasticsearch:** localhost:9200

---

## Common Tasks

### Add Team Member
```bash
POST /api/v1/projects/{id}/team/invite
Body: { "user_email": "user@example.com", "role": "analyst" }
```

### Create Custom Dashboard
```bash
POST /api/v1/dashboards
Body: {
  "name": "My Dashboard",
  "project_id": 1,
  "widgets": [
    {
      "widget_type": "seo_score",
      "title": "SEO Score",
      "width": 4,
      "height": 4
    }
  ]
}
```

### Upload URL List
```bash
POST /api/v1/projects/{id}/list-crawl/upload
Content-Type: multipart/form-data
file: urls.csv
```

---

## Comparison: You vs Screaming Frog

| Feature | Screaming Frog | Your Platform |
|---------|----------------|---------------|
| Desktop/Web | Desktop | **Web-based** ✨ |
| JS Rendering | ✅ | ✅ |
| Core Web Vitals | ✅ v23 | ✅ |
| List Mode | ✅ | ✅ |
| Log Analysis | ✅ Separate tool | ✅ Integrated |
| Accessibility | ✅ v21+ | ✅ |
| Excel Export | ✅ Basic | ✅ **Advanced** ✨ |
| **SERP Tracking** | ❌ | ✅ **Unique** 🏆 |
| **AI Features** | ❌ | ✅ **Unique** 🏆 |
| **Team Collaboration** | ❌ | ✅ **Unique** 🏆 |
| **Continuous Monitoring** | ❌ | ✅ **Unique** 🏆 |
| **Custom Dashboards** | ❌ | ✅ **Unique** 🏆 |
| **Historical Tracking** | ❌ | ✅ **Unique** 🏆 |
| Price | $259/year | **Free** (self-hosted) 🎉 |

---

## Next Steps

1. Configure API keys in `.env`
2. Run `docker-compose up -d`
3. Run migrations
4. Access http://localhost
5. Create your first project
6. Start crawling!

**You now have a platform that matches AND exceeds Screaming Frog!** 🚀
