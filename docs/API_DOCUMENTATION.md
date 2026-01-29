# API Documentation - SEO Analysis Platform

## Base URL

```
http://localhost/api/v1
```

## Authentication

All endpoints (except auth) require JWT authentication via Bearer token:

```
Authorization: Bearer <access_token>
```

---

## API Endpoints Overview

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token

### Projects
- `GET /projects` - List all projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Crawling
- `POST /projects/{id}/crawl` - Start crawl
- `GET /crawls/{id}` - Get crawl status
- `POST /projects/{id}/list-crawl` - List mode crawling
- `POST /projects/{id}/list-crawl/upload` - Upload URL list (CSV/Excel)

### Team Collaboration
- `POST /projects/{id}/team/invite` - Invite team member
- `GET /projects/{id}/team` - List team members
- `DELETE /projects/{id}/team/{user_id}` - Remove member
- `POST /projects/{id}/comments` - Add comment
- `GET /projects/{id}/comments` - Get comments
- `POST /projects/{id}/tasks` - Create task
- `GET /projects/{id}/tasks` - List tasks
- `PUT /tasks/{id}` - Update task

### Custom Dashboards
- `POST /dashboards` - Create dashboard
- `GET /dashboards` - List dashboards
- `GET /dashboards/{id}` - Get dashboard
- `PUT /dashboards/{id}` - Update dashboard
- `DELETE /dashboards/{id}` - Delete dashboard
- `POST /dashboards/{id}/widgets` - Add widget
- `PUT /dashboards/{id}/widgets/{widget_id}` - Update widget
- `DELETE /dashboards/{id}/widgets/{widget_id}` - Delete widget
- `GET /widgets/types` - Get available widget types

### Monitoring & Alerts
- `POST /projects/{id}/monitoring/start` - Start monitoring
- `POST /projects/{id}/monitoring/stop` - Stop monitoring
- `GET /projects/{id}/monitoring/status` - Get status
- `POST /projects/{id}/schedule` - Create schedule
- `GET /alerts` - Get alerts
- `PUT /alerts/{id}/acknowledge` - Acknowledge alert

### SERP Tracking
- `POST /keywords` - Add keywords to track
- `GET /keywords` - List tracked keywords
- `POST /keywords/check` - Check rankings
- `GET /keywords/{id}/history` - Get ranking history
- `GET /keywords/{id}/competitors` - Get competitor rankings

### Competitive Analysis
- `POST /projects/{id}/competitors/add` - Add competitor
- `GET /projects/{id}/competitors` - List competitors
- `POST /projects/{id}/competitors/compare` - Compare with competitors
- `GET /projects/{id}/gaps` - Get content gaps

### AI-Powered Features
- `POST /ai/content-score` - Score content quality
- `POST /ai/alt-text/generate` - Generate alt text
- `POST /ai/alt-text/batch` - Batch generate alt text
- `POST /ai/content-brief` - Generate content brief

### Advanced Analysis
- `POST /analysis/lighthouse` - Run Lighthouse audit
- `POST /analysis/accessibility` - Run accessibility audit
- `POST /analysis/duplicates` - Detect duplicate content
- `POST /analysis/images` - Analyze image
- `POST /analysis/redirect-chains` - Analyze redirect chain
- `POST /logs/upload` - Upload server log file

### Export & Reporting
- `GET /projects/{id}/export/excel` - Export to Excel
- `GET /projects/{id}/export/sitemap` - Generate sitemap
- `GET /projects/{id}/export/csv` - Export to CSV

---

## Example Requests

### Start a Crawl with JavaScript Rendering

```bash
curl -X POST http://localhost/api/v1/projects/1/crawl \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"enable_js": true}'
```

### Check Keyword Rankings

```bash
curl -X POST http://localhost/api/v1/keywords/check \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["seo tools", "keyword research"],
    "location": "United States",
    "project_id": 1
  }'
```

### Generate Alt Text with AI

```bash
curl -X POST http://localhost/api/v1/ai/alt-text/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "context": {"page_topic": "SEO Guide"}
  }'
```

### Run Lighthouse Audit

```bash
curl -X POST http://localhost/api/v1/analysis/lighthouse \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "categories": ["performance", "accessibility", "seo"]
  }'
```

---

## Interactive Documentation

Full interactive API documentation available at:
- **Swagger UI:** http://localhost/docs
- **ReDoc:** http://localhost/redoc

---

## Rate Limits

- SERP API: 2000 requests/day (Google Search Console limit)
- AI Features: Depends on OpenAI plan
- Standard API: No hard limits (be respectful)

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `500` - Server error
