# 🚀 LuminaryAI Deployment Guide

Complete guide for deploying LuminaryAI in production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Production Checklist](#production-checklist)
6. [Monitoring](#monitoring)
7. [Scaling](#scaling)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Python 3.11+**
- **PostgreSQL 12+** (for production) or SQLite (for development)
- **Redis 6+** (optional, for caching and rate limiting)
- **Docker & Docker Compose** (recommended)
- **API Keys**:
  - Google Gemini API key

### Optional

- **Nginx** (reverse proxy)
- **Systemd** (service management)
- **Prometheus & Grafana** (monitoring)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Agentic_Law_AI
```

### 2. Configure Environment Variables

```bash
# Copy example file
cp env.example .env

# Edit .env file
nano .env
```

**Required variables:**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### 3. Generate Secret Keys

```bash
# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate Flask secret key
openssl rand -hex 32
```

---

## Docker Deployment (Recommended)

### Quick Start

```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit .env and add your API keys
nano .env

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f backend
```

### Services

- **Backend**: `http://localhost:5000`
- **Frontend**: `http://localhost:8501`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

### Quick Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

### Production Docker Compose

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

---

## Manual Deployment

### 1. Install Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Setup Database

**SQLite (Development):**
```bash
python -c "from models import init_db; init_db()"
```

**PostgreSQL (Production):**
```sql
CREATE DATABASE luminary;
CREATE USER luminary WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE luminary TO luminary;
```

Update `.env`:
```env
DATABASE_URL=postgresql://luminary:your_password@localhost:5432/luminary
```

### 3. Initialize Database

```bash
python -c "from models import init_db; init_db('$DATABASE_URL')"
```

### 4. Run with Gunicorn

```bash
# Development
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 app:app

# Production with more workers
gunicorn --bind 0.0.0.0:5000 \
         --workers 8 \
         --threads 4 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --log-level info \
         --preload \
         app:app
```

### 5. Run Frontend

```bash
streamlit run main.py --server.port=8501
```

---

## Production Checklist

### Security

- [ ] Change all default secret keys
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Use environment variables (not hardcoded secrets)
- [ ] Enable security headers
- [ ] Regular security updates

### Database

- [ ] Use PostgreSQL for production
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Enable SSL connections

### Application

- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper logging
- [ ] Set up log rotation
- [ ] Enable health checks
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificates

### Monitoring

- [ ] Set up application monitoring
- [ ] Configure error tracking (Sentry)
- [ ] Set up log aggregation
- [ ] Configure alerts
- [ ] Monitor API usage

---

## Nginx Configuration

### Reverse Proxy Setup

```nginx
upstream luminary_backend {
    server 127.0.0.1:5000;
}

upstream luminary_frontend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API
    location /api/ {
        proxy_pass http://luminary_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Frontend
    location / {
        proxy_pass http://luminary_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Systemd Service

### Backend Service

Create `/etc/systemd/system/luminary-backend.service`:

```ini
[Unit]
Description=LuminaryAI Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/luminary
Environment="PATH=/opt/luminary/venv/bin"
EnvironmentFile=/opt/luminary/.env
ExecStart=/opt/luminary/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 8 \
    --threads 4 \
    --timeout 120 \
    --access-logfile /var/log/luminary/access.log \
    --error-logfile /var/log/luminary/error.log \
    app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable luminary-backend
sudo systemctl start luminary-backend
sudo systemctl status luminary-backend
```

---

## Monitoring

### Health Checks

```bash
# Check health
curl http://localhost:5000/api/health

# Check status
curl http://localhost:5000/api/status
```

### Logs

```bash
# Application logs
tail -f logs/luminary.log

# Error logs
tail -f logs/luminary_errors.log

# Gunicorn logs
tail -f logs/access.log
tail -f logs/error.log
```

### Metrics

Monitor:
- Request rate
- Response times
- Error rates
- Database connections
- Memory usage
- CPU usage
- API quota usage

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or AWS ALB
2. **Multiple Workers**: Increase Gunicorn workers
3. **Database**: Read replicas for PostgreSQL
4. **Cache**: Redis for session storage and caching

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Add caching layer
4. Use CDN for static assets

---

## Backup Strategy

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U luminary luminary > backup_$(date +%Y%m%d).sql

# Restore
psql -U luminary luminary < backup_20250101.sql
```

### File Backups

```bash
# Backup uploads and storage
tar -czf backup_files_$(date +%Y%m%d).tar.gz uploads/ chromadb_storage/ document_storage/
```

### Automated Backups

Set up cron job:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/luminary/scripts/backup.sh
```

---

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

**2. Database Connection Error**
- Check database is running
- Verify credentials in `.env`
- Check firewall rules

**3. AI Service Not Available**
- Verify `GOOGLE_API_KEY` is set
- Check API quota
- Review error logs

**4. Rate Limiting Issues**
- Check Redis is running (if enabled)
- Verify rate limit configuration
- Check logs for rate limit errors

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug
FLASK_ENV=development python app.py
```

---

## Performance Tuning

### Gunicorn Workers

```python
# Formula: (2 × CPU cores) + 1
workers = (2 * cpu_count()) + 1
```

### Database Pool

```python
# SQLAlchemy connection pool
DATABASE_POOL_SIZE = 10
DATABASE_MAX_OVERFLOW = 20
```

### Redis Configuration

```redis
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

---

## Support

For issues or questions:
- Check logs: `logs/luminary.log`
- Review health check: `/api/health`
- Check status: `/api/status`

---

**Last Updated**: 2025-01-01  
**Version**: 2.0.0

