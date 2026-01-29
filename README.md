# SEORankPulse

A comprehensive SEO analysis platform that combines traditional technical auditing with modern AI-powered insights. Built as a portfolio project to demonstrate full-stack development skills with enterprise-grade architecture.

## What It Does

SEORankPulse crawls websites and provides detailed SEO analysis reports. Think of it as a self-hosted alternative to tools like Screaming Frog or Sitebulb, but with added AI capabilities for content analysis and semantic understanding.

The platform handles everything from basic technical SEO (broken links, meta tags, redirects) to advanced features like graph-based link analysis, duplicate content detection, and AI-driven content scoring.

## Core Features

**Web Crawler**
- Asynchronous crawling engine built with Python's httpx and asyncio
- JavaScript rendering support via Playwright for SPAs
- Respects robots.txt and handles rate limiting
- Can resume interrupted crawls

**Technical SEO Analysis**
- HTTP status codes and redirect chains
- Meta tags and heading structure validation
- Image optimization checks (file size, alt tags)
- Core Web Vitals integration via Lighthouse
- Duplicate content detection using fuzzy hashing

**AI-Powered Analysis**
- Content semantic analysis with Hugging Face transformers
- Named entity recognition for topic extraction
- Sentiment analysis via Google Cloud NLP
- Automated alt text generation for images

**Link Graph Analysis**
- Internal link structure stored in Neo4j graph database
- PageRank calculation to identify important pages
- Orphan page detection
- Hub and authority identification

**Additional Tools**
- SERP tracking for keyword positions
- Google Search Console integration
- Competitive gap analysis
- Server log analysis
- Excel/sitemap export

## Tech Stack

Built with technologies I wanted to learn and demonstrate proficiency in:

**Backend**
- FastAPI for async REST APIs
- PostgreSQL (SQLAlchemy 2.0 async ORM)
- Neo4j for graph data
- Elasticsearch for full-text search
- Redis + Celery for background jobs
- Alembic for database migrations

**Frontend**
- Next.js 14 with App Router
- TypeScript throughout
- Tailwind CSS + Shadcn/UI components
- Recharts for data visualization

**Infrastructure**
- Fully dockerized with docker-compose
- Nginx as reverse proxy
- GitHub Actions for CI/CD
- Environment-based configuration

## Getting Started

You'll need Docker and Docker Compose installed.

```bash
# Clone the repo
git clone https://github.com/syeedalireza/seorankpulse.git
cd seorankpulse

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys if you want AI features
# The platform works without them, just won't have AI analysis

# Start everything
docker-compose up -d

# Wait a minute for databases to initialize, then visit:
# http://localhost - Frontend dashboard
# http://localhost/api/docs - API documentation
```

The first startup takes a few minutes while Docker pulls images and initializes databases.

## Development Setup

If you want to run services locally for development:

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

You'll still need the databases running via docker-compose (PostgreSQL, Redis, Neo4j, Elasticsearch).

## Architecture

The system follows a microservices-inspired architecture where the FastAPI backend acts as an API gateway, coordinating between different services:

- **Web Crawler**: Fetches and parses web pages
- **Analysis Engine**: Processes page data for SEO issues
- **AI Services**: Content scoring and semantic analysis
- **Graph Engine**: Link structure analysis in Neo4j
- **SERP Tracker**: Keyword ranking monitoring
- **Export Service**: Report generation

Background tasks run via Celery workers, which handle time-intensive operations like crawling entire sites or running Lighthouse audits.

## API

RESTful API with JWT authentication. Interactive docs at `/api/docs`.

Key endpoints:
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/projects` - Create new project
- `POST /api/v1/crawls/start` - Start website crawl
- `GET /api/v1/analysis/{crawl_id}` - Get analysis results
- `GET /api/v1/graph/{crawl_id}` - Get link graph data

Full API documentation is available in the Swagger UI when the application is running.

## Testing

Backend has pytest tests for core functionality:

```bash
cd backend
pytest
```

Tests cover crawling logic, analysis algorithms, API endpoints, and database operations.

## Project Status

This is a portfolio project built to showcase full-stack development skills. It's functional and demonstrates various technologies and architectural patterns, but it's not production-ready for large-scale commercial use.

Current test coverage is around 60%. The focus was on implementing diverse features rather than achieving 100% coverage on everything.

## Why I Built This

I wanted a project that would demonstrate:
- Full-stack development (Python backend, TypeScript frontend)
- Async programming patterns
- Database design (relational + graph + document stores)
- Background job processing
- API design
- Docker and DevOps practices
- Integration with third-party APIs
- Complex algorithm implementation (PageRank, duplicate detection)

SEO analysis was chosen because it requires a good mix of web scraping, data processing, and visualization - plus it's actually useful.

## License

MIT License - feel free to use this code for learning or as a starting point for your own projects.

## Contact

**Syed Ali Reza**
- GitHub: [@syeedalireza](https://github.com/syeedalireza)

Questions or feedback? Open an issue or reach out via GitHub.
