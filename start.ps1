# راه‌اندازی خودکار SEO Platform

Write-Host "🚀 SEO Analysis Platform - Auto Start Script" -ForegroundColor Green
Write-Host ""

# چک کردن Docker databases
Write-Host "📊 Checking databases..." -ForegroundColor Yellow
$containers = docker-compose -f docker-compose.simple.yml ps -q
if ($containers.Count -eq 0) {
    Write-Host "Starting databases..." -ForegroundColor Yellow
    docker-compose -f docker-compose.simple.yml up -d
    Start-Sleep -Seconds 10
}

Write-Host "✅ Databases are running!" -ForegroundColor Green
Write-Host ""

# راه‌اندازی Backend
Write-Host "🔧 Starting Backend..." -ForegroundColor Yellow
cd backend

# تنظیم environment variables
$env:DATABASE_URL="postgresql+asyncpg://seo_user:seo_password@localhost:5432/seo_db"
$env:SECRET_KEY="dev-secret-key-change-in-production"
$env:JWT_SECRET_KEY="dev-jwt-secret-key-change-in-production"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_USER="seo_user"
$env:POSTGRES_PASSWORD="seo_password"
$env:POSTGRES_DB="seo_db"
$env:REDIS_HOST="localhost"
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="neo4j_password"
$env:ELASTICSEARCH_HOST="localhost:9200"

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow

# چک virtual environment
if (-Not (Test-Path "venv")) {
    python -m venv venv
}

.\venv\Scripts\activate
pip install -q -r requirements.txt

Write-Host "Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

Write-Host "✅ Backend ready! Starting server..." -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\development\seo\backend; .\venv\Scripts\activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd ..

# راه‌اندازی Frontend
Write-Host "🎨 Starting Frontend..." -ForegroundColor Yellow
cd frontend

Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
npm install

$env:NEXT_PUBLIC_API_URL="http://localhost:8000"

Write-Host "✅ Frontend ready! Starting dev server..." -ForegroundColor Green
Write-Host "Frontend Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Start frontend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\development\seo\frontend; npm run dev"

cd ..

Write-Host ""
Write-Host "🎉 SEO Platform is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Neo4j:     http://localhost:7474" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Wait 30-60 seconds for services to fully start..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Red
