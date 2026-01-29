# 🚀 SEORankPulse

**The Ultimate AI-Powered SEO Analysis Platform**

A cutting-edge, enterprise-grade SEO analysis tool built with modern technologies and best practices. SEORankPulse provides comprehensive technical SEO audits, AI-driven content analysis, and advanced link graph visualization to help you dominate search rankings.

## ✨ Key Features

### 🔍 Advanced Web Crawler
- Asynchronous crawling with JavaScript rendering support
- Intelligent robots.txt and sitemap.xml parsing
- Resume capability for interrupted crawls
- Rate limiting and politeness controls

### 🤖 AI-Powered Analysis
- **Semantic Content Analysis**: Using Hugging Face transformers for meaning extraction
- **Named Entity Recognition**: Automatic extraction of persons, locations, and organizations
- **Sentiment Analysis**: Content tone evaluation with Google Cloud NLP
- **Topic Modeling**: Automatic content categorization

### 📊 Link Graph Intelligence
- Neo4j-powered graph database for link structure
- Internal PageRank calculation
- Hub and Authority page identification
- Orphan page detection
- Visual graph representation

### 🎯 Technical SEO Audits
- HTTP status code analysis (404s, redirects, errors)
- Meta tags validation (title, description)
- Heading structure analysis
- Image alt tag verification
- Duplicate content detection
- Core Web Vitals monitoring

### 📈 Comprehensive Dashboard
- Real-time crawl status monitoring
- Interactive data visualizations
- Exportable reports (PDF/Excel)
- Multi-project management
- API key management

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async Python web framework
- **PostgreSQL**: Primary relational database
- **Neo4j**: Graph database for link analysis
- **Elasticsearch**: Full-text search and content indexing
- **Redis**: Task queue and caching
- **Celery**: Distributed task processing
- **SQLAlchemy 2.0**: Async ORM
- **Pydantic v2**: Data validation

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Shadcn/UI**: Modern component library
- **TailwindCSS**: Utility-first CSS framework
- **Recharts & D3.js**: Interactive data visualization
- **Zustand**: Lightweight state management
- **React Query**: Server state management

### AI/ML Services
- **Hugging Face Inference API**: NLP models
- **Google Cloud Natural Language API**: Advanced text analysis
- **OpenAI API**: Content generation (optional)

## 📦 Installation

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/seo-analysis-platform.git
cd seo-analysis-platform
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start the services**
```bash
docker-compose up -d
```

4. **Access the platform**
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js UI     │
└────────┬────────┘
         │
         │ REST API
         │
┌────────▼────────┐
│  FastAPI        │
│  API Gateway    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼──┐ ┌─────▼────┐ ┌──▼────┐
│Crawler│ │AI   │ │Graph     │ │Keyword│
│Service│ │Anal-│ │Analysis  │ │Tracker│
│       │ │yzer │ │          │ │       │
└───┬───┘ └──┬──┘ └─────┬────┘ └──┬────┘
    │        │          │         │
    │     ┌──▼──────────▼─────────▼──┐
    │     │  Celery Workers + Redis  │
    │     └──┬──────────┬────────────┘
    │        │          │
┌───▼────┬───▼───┐ ┌───▼────┐
│Postgre │ Neo4j │ │Elastic │
│SQL     │ Graph │ │search  │
└────────┴───────┘ └────────┘
```

## 🔧 Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/v1/auth/register       - User registration
POST   /api/v1/auth/login          - User login
GET    /api/v1/projects            - List projects
POST   /api/v1/projects            - Create project
POST   /api/v1/projects/{id}/crawl - Start crawl
GET    /api/v1/analysis/{id}       - Get analysis results
GET    /api/v1/graph/{id}          - Get link graph data
```

## 🧪 Code Quality

This project follows industry best practices:

- **Type Safety**: Full type hints in Python, TypeScript in frontend
- **Code Formatting**: Black, isort, Prettier
- **Linting**: Flake8, ESLint
- **Testing**: pytest (80%+ coverage target), Jest
- **Architecture**: Clean Architecture, Domain-Driven Design
- **Documentation**: Comprehensive docstrings (Google style)

## 📊 Database Schema

### PostgreSQL
- Users, Projects, Crawl Jobs
- Pages, Issues, Reports

### Neo4j Graph
- Nodes: Pages
- Relationships: LINKS_TO

### Elasticsearch
- Document: Page Content
- Indexed for full-text search

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- Neo4j for graph database capabilities
- Hugging Face for AI model access
- The open-source community

---

Built with ❤️ using modern technologies and best practices.
