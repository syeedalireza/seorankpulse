# Complete Features Guide - SEO Analysis Platform

## Table of Contents

1. [JavaScript Rendering](#javascript-rendering)
2. [Lighthouse & Core Web Vitals](#lighthouse--core-web-vitals)
3. [List Mode Crawling](#list-mode-crawling)
4. [XML Sitemap Generation](#xml-sitemap-generation)
5. [Google Search Console Integration](#google-search-console-integration)
6. [Advanced Excel Export](#advanced-excel-export)
7. [Server Log Analysis](#server-log-analysis)
8. [Duplicate Content Detection](#duplicate-content-detection)
9. [Image Analysis](#image-analysis)
10. [Accessibility Audits](#accessibility-audits)
11. [Redirect Chain Analysis](#redirect-chain-analysis)
12. [Historical Tracking & Alerts](#historical-tracking--alerts)
13. [AI Content Scoring](#ai-content-scoring)
14. [AI Alt Text Generation](#ai-alt-text-generation)
15. [Continuous Monitoring](#continuous-monitoring)
16. [Competitive Analysis](#competitive-analysis)
17. [SERP Position Tracking](#serp-position-tracking)
18. [Team Collaboration](#team-collaboration)
19. [Custom Dashboards](#custom-dashboards)

---

## JavaScript Rendering

### Overview
Crawl and analyze JavaScript-heavy websites (React, Vue, Angular, Next.js) using Playwright/Chromium.

### Usage

```python
from app.services.crawler.spider import WebCrawler

# Enable JS rendering
crawler = WebCrawler(project, enable_js=True)
async with crawler:
    results = await crawler.crawl()
```

### API Endpoint

```bash
POST /api/v1/projects/{id}/crawl
{
  "enable_js": true
}
```

### Benefits
- Accurate SEO analysis of SPAs
- Detects JavaScript-rendered content
- Identifies client-side frameworks
- Measures JavaScript performance

---

## Lighthouse & Core Web Vitals

### Overview
Run Google Lighthouse audits to measure Core Web Vitals (LCP, FID, CLS) and performance metrics.

### Usage

```python
from app.services.lighthouse import run_lighthouse_audit

results = await run_lighthouse_audit(url="https://example.com")

print(f"Performance Score: {results['scores']['performance']}")
print(f"LCP: {results['core_web_vitals']['lcp']}s")
```

### API Endpoint

```bash
POST /api/v1/analysis/lighthouse
{
  "url": "https://example.com",
  "categories": ["performance", "accessibility", "seo"]
}
```

### Metrics Provided
- **Performance Score** (0-100)
- **LCP** - Largest Contentful Paint
- **FID** - First Input Delay
- **CLS** - Cumulative Layout Shift
- **FCP** - First Contentful Paint
- **TTI** - Time to Interactive
- **TBT** - Total Blocking Time
- Optimization opportunities

---

## List Mode Crawling

### Overview
Analyze specific URLs without crawling entire site. Upload CSV/Excel files with URLs.

### Supported File Formats
- CSV (.csv)
- Excel (.xlsx, .xls)
- Plain Text (.txt)

### Usage

```bash
POST /api/v1/projects/{id}/list-crawl/upload
Content-Type: multipart/form-data

file: urls.csv
url_column: url
enable_js: false
```

### CSV Format

```csv
url,priority
https://example.com/page1,high
https://example.com/page2,medium
```

---

## XML Sitemap Generation

### Overview
Automatically generate XML sitemaps from crawl results.

### Features
- Standard sitemap.xml
- Sitemap index for large sites (>50K URLs)
- Automatic priority calculation
- Change frequency hints
- Last modified dates

### Usage

```python
from app.services.export import generate_sitemap_with_index

result = generate_sitemap_with_index(
    domain="example.com",
    pages=pages_data
)

# Single sitemap
if result['index'] is None:
    sitemap_xml = result['sitemaps'][0]

# Multiple sitemaps with index
else:
    for idx, sitemap in enumerate(result['sitemaps']):
        # Save as sitemap1.xml, sitemap2.xml, etc.
        pass
    
    sitemap_index = result['index']
```

### API Endpoint

```bash
GET /api/v1/projects/{id}/export/sitemap
```

---

## Google Search Console Integration

### Overview
Connect to Google Search Console API for URL inspection and search analytics data.

### Setup

1. Create Google Cloud project
2. Enable Search Console API
3. Download credentials JSON
4. Set environment variables:

```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
GSC_CREDENTIALS_FILE=/path/to/credentials.json
```

### Features
- URL Inspection (up to 2000/day per property)
- Indexing status
- Mobile usability
- Search analytics data
- Top queries and pages
- Sitemap submission

---

## Advanced Excel Export

### Overview
Export comprehensive SEO reports to Excel with multiple sheets.

### Sheets Included
1. **Summary** - Key metrics and statistics
2. **All Pages** - Complete page data
3. **Issues** - Detected SEO issues
4. **Status Codes** - Distribution with pie chart
5. **Redirects** - All redirect pages
6. **Errors** - 4xx and 5xx errors
7. **Meta Data** - Title and description analysis
8. **Images** - Image optimization data

### Features
- Color-coded cells (green/yellow/red)
- Auto-filters on all data sheets
- Frozen header rows
- Charts and visualizations
- Professional formatting

---

## Server Log Analysis

### Overview
Parse and analyze Apache/Nginx server logs for SEO insights.

### Supported Formats
- Apache Combined Log Format
- Nginx default format
- Auto-detection

### Analyses Provided
- **Bot Traffic Analysis** - Googlebot, Bingbot, etc.
- **Crawl Budget** - Requests per day by bot
- **Status Code Distribution**
- **Error URLs** - Most frequently erroring pages
- **Popular Pages** - Most requested pages
- **Time Patterns** - Hourly/daily distribution

### Usage

```bash
POST /api/v1/logs/upload
Content-Type: multipart/form-data

file: access.log
log_format: auto
project_id: 1
```

---

## Duplicate Content Detection

### Overview
Detect exact and near-duplicate content using SimHash algorithm.

### Algorithm
- **SimHash** for near-duplicate detection
- **MD5 Hashing** for exact duplicates
- Configurable similarity threshold

### Usage

```bash
POST /api/v1/analysis/duplicates
{
  "project_id": 1,
  "similarity_threshold": 3
}
```

### Threshold Guide
- `1-2` - Very strict (only very similar content)
- `3-5` - Moderate (recommended)
- `6-10` - Loose (catches more variations)

---

## Image Analysis

### Overview
Analyze images for optimization opportunities.

### Checks Performed
- File size and format
- Image dimensions
- Compression potential
- Format recommendations (WebP, AVIF)
- Duplicate image detection (perceptual hash)
- Bytes-per-pixel ratio

### Recommendations
- Convert to WebP/AVIF
- Resize oversized images
- Use progressive JPEG
- Implement responsive images (srcset)

---

## Accessibility Audits

### Overview
WCAG 2.1 compliance checking using AXE engine.

### Compliance Levels
- **Level A** - Basic accessibility
- **Level AA** - Mid-range accessibility (recommended)
- **Level AAA** - Enhanced accessibility

### Violation Categories
- **Critical** - Major barriers
- **Serious** - Significant barriers
- **Moderate** - Noticeable barriers
- **Minor** - Minor issues

### Usage

```bash
POST /api/v1/analysis/accessibility
{
  "url": "https://example.com",
  "tags": ["wcag2a", "wcag2aa"]
}
```

---

## Redirect Chain Analysis

### Overview
Track and visualize redirect chains to optimize crawl budget.

### Detects
- Redirect loops
- Long chains (>3 hops)
- Temporary vs permanent redirects
- HTTP/HTTPS mixed protocols
- Cross-domain redirects

### Issues Flagged
- Chains >3 hops (slows down crawling)
- 302 redirects (should be 301 for SEO)
- Redirect loops (critical)

---

## Historical Tracking & Alerts

### Overview
Track SEO metrics over time and get alerts for significant changes.

### Tracked Metrics
- SEO scores
- Error counts
- Performance metrics
- Issue counts
- Ranking changes

### Alert Triggers
- SEO score drops >10%
- New errors detected
- Performance degradation
- Critical issues found

### Alert Channels
- Email
- Slack
- Webhooks

---

## AI Content Scoring

### Overview
Use GPT-4/Claude to evaluate content quality and get improvement suggestions.

### Analysis Provided
- Overall quality score (0-100)
- Readability assessment
- SEO optimization analysis
- E-A-T evaluation
- Engagement potential
- Improvement recommendations

### Usage

```bash
POST /api/v1/ai/content-score
{
  "content": "Your page content here...",
  "url": "https://example.com/page",
  "target_keyword": "seo tools"
}
```

---

## AI Alt Text Generation

### Overview
Automatically generate descriptive alt text for images using Vision AI.

### Features
- GPT-4 Vision integration
- Context-aware descriptions
- SEO-optimized alt text
- Batch processing
- Alt text validation

### Usage

```bash
POST /api/v1/ai/alt-text/generate
{
  "image_url": "https://example.com/image.jpg",
  "context": {
    "page_topic": "SEO Guide",
    "surrounding_text": "This screenshot shows..."
  },
  "max_length": 125
}
```

---

## Continuous Monitoring

### Overview
Automated scheduled crawls with change detection and alerting.

### Frequencies
- Hourly
- Daily
- Weekly
- Monthly
- Custom

### Features
- Automatic crawl execution
- Metric comparison
- Anomaly detection
- Alert generation
- Historical trends

---

## Competitive Analysis

### Overview
Compare your site with competitors on key SEO metrics.

### Comparison Metrics
- SEO scores
- Response times
- Error rates
- Content length
- Accessibility scores
- Performance metrics

### Features
- Multi-site comparison
- Competitive matrix
- Strength/weakness identification
- Content gap analysis
- Page type comparison

---

## SERP Position Tracking

### Overview
Track keyword rankings in Google search results.

### Features
- Keyword ranking tracking
- Competitor monitoring
- SERP feature detection
- Historical ranking data
- Ranking change alerts

### SERP Features Detected
- Featured snippets
- Knowledge graph
- Local pack
- People also ask
- Image pack
- Video results

---

## Team Collaboration

### Overview
Collaborate with team members on SEO projects.

### Roles
- **Owner** - Full access
- **Admin** - Manage team and settings
- **Analyst** - View and analyze
- **Viewer** - Read-only access

### Features
- Team member invitation
- Page comments
- Task assignment
- Task tracking (todo, in_progress, done)
- Priority levels (low, medium, high, critical)

---

## Custom Dashboards

### Overview
Create personalized dashboards with drag-and-drop widgets.

### Available Widgets
- SEO Score
- Status Code Chart
- Top Pages
- Error Pages
- Keyword Rankings
- Duplicate Content
- Accessibility Score
- Recent Alerts
- Competitor Comparison
- Response Time Trend
- Custom Text Notes

### Widget Categories
- Overview
- Charts
- Lists
- Analysis
- Rankings
- Alerts
- Custom

---

## Quick Start Examples

### Run Complete SEO Audit

```python
# 1. Start crawl with JS
crawler = WebCrawler(project, enable_js=True)
results = await crawler.crawl()

# 2. Run Lighthouse on key pages
lighthouse_results = await run_lighthouse_audit(url)

# 3. Check accessibility
accessibility_results = await audit_accessibility(url)

# 4. Detect duplicates
duplicates = detect_duplicates(pages)

# 5. Generate report
excel_file = export_to_excel(pages, summary, issues, project.name)
```

### Setup Continuous Monitoring

```python
# 1. Create monitoring schedule
monitor = ContinuousMonitor(project_id)
await monitor.start_monitoring(
    frequency=ScheduleFrequency.DAILY,
    alert_thresholds={
        'seo_score_drop': 10,
        'error_increase': 5,
    }
)

# 2. Alerts will be sent automatically when thresholds are exceeded
```

### Track Keyword Rankings

```python
# 1. Add keywords
client = SerpAPIClient(api_key)
rankings = await client.check_rankings(
    keywords=['seo tools', 'keyword research'],
    domain='example.com',
    location='United States'
)

# 2. Schedule daily checks
# (Automatically runs via Celery Beat)
```

---

## Configuration

### Required Environment Variables

```bash
# Core Services
POSTGRES_*
REDIS_*
NEO4J_*
ELASTICSEARCH_*

# AI Features (Optional but recommended)
OPENAI_API_KEY=sk-...
GOOGLE_CLOUD_API_KEY=...

# SERP Tracking (Optional)
SERP_API_KEY=...

# Monitoring (Optional)
SLACK_WEBHOOK_URL=...
EMAIL_SMTP_*
```

### Optional Features

Most features work without API keys:
- Basic crawling ✅
- Technical SEO ✅
- Link analysis ✅

AI features require:
- Content scoring → OpenAI API key
- Alt text generation → OpenAI API key
- SERP tracking → SerpAPI key

---

## Performance Considerations

### Scalability
- **Concurrent Crawls:** Configure `CRAWLER_CONCURRENT_REQUESTS`
- **Celery Workers:** Scale horizontally (add more worker containers)
- **Database:** PostgreSQL can handle millions of pages
- **Caching:** Redis for fast access

### Best Practices
- Enable JS rendering only when needed (slower)
- Use list mode for quick checks
- Schedule intensive tasks during off-hours
- Limit Lighthouse audits (slow and resource-intensive)
- Batch AI requests to optimize costs

---

## Troubleshooting

### JavaScript Rendering Issues
- Ensure Playwright is installed: `playwright install chromium`
- Check Playwright service is running in Docker
- Increase timeout if pages are slow

### Lighthouse Errors
- Requires Node.js and `lighthouse` npm package
- Run `npm install -g lighthouse`
- Check Chrome/Chromium is available

### API Key Issues
- Verify API keys in `.env` file
- Check API key has correct permissions
- Monitor API quotas and limits

### Performance Issues
- Reduce concurrent requests
- Enable caching
- Use PostgreSQL connection pooling
- Scale Celery workers

---

## Support & Resources

- **API Documentation:** http://localhost/docs
- **Flower (Celery Monitoring):** http://localhost:5555
- **Neo4j Browser:** http://localhost:7474
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/seo-platform)

---

**Last Updated:** January 28, 2026
**Version:** 2.0.0 (Screaming Frog Enhanced)
