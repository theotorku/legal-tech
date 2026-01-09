# Deployment Guide

This guide covers deploying the Contract Analyzer API to production.

## Pre-Deployment Checklist

- [ ] OpenAI API key configured
- [ ] Supabase database set up (optional)
- [ ] Environment variables configured
- [ ] SSL/TLS certificates ready
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place

## Environment Setup

### 1. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

**Required variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `ENVIRONMENT`: Set to `production`

**Optional but recommended:**
- `SUPABASE_URL`: For data persistence
- `SUPABASE_KEY`: Supabase API key
- `RATE_LIMIT_PER_MINUTE`: Adjust based on your needs
- `LOG_LEVEL`: Set to `INFO` or `WARNING` in production

### 2. Database Setup (Optional)

If using Supabase:

1. Create a Supabase project
2. Run the SQL in `supabase_sql.sql` in the SQL editor
3. Copy your project URL and API key to `.env`

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Advantages:**
- Easy to deploy and manage
- Consistent environment
- Built-in health checks

**Steps:**

1. Build and start:
```bash
docker-compose up -d
```

2. Check logs:
```bash
docker-compose logs -f
```

3. Check health:
```bash
curl http://localhost:8000/health
```

### Option 2: Docker

**Steps:**

1. Build image:
```bash
docker build -t contract-analyzer:latest .
```

2. Run container:
```bash
docker run -d \
  --name contract-analyzer \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  contract-analyzer:latest
```

### Option 3: Direct Python Deployment

**Steps:**

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run with Gunicorn (production WSGI server):
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## Reverse Proxy Setup

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;

    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Monitoring

### Health Checks

The API provides a `/health` endpoint for monitoring:

```bash
curl https://your-domain.com/health
```

### Logging

Logs are output in JSON format (configurable via `LOG_FORMAT`):

```bash
# View logs with Docker
docker-compose logs -f

# View logs with journalctl (systemd)
journalctl -u contract-analyzer -f
```

### Metrics

Monitor these key metrics:
- Request rate
- Error rate
- Response time (p50, p95, p99)
- OpenAI API latency
- Database connection pool

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```bash
docker-compose up -d --scale api=3
```

### Vertical Scaling

Adjust worker count based on CPU cores:

```bash
# In Dockerfile or docker-compose.yml
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

## Security Best Practices

1. **Use HTTPS**: Always use TLS/SSL in production
2. **API Keys**: Store in environment variables, never in code
3. **Rate Limiting**: Configure appropriate limits
4. **CORS**: Restrict to specific origins in production
5. **Updates**: Keep dependencies updated
6. **Monitoring**: Set up alerts for errors and anomalies

## Troubleshooting

### Common Issues

**Issue: High memory usage**
- Solution: Reduce worker count or use smaller model

**Issue: Slow response times**
- Solution: Check OpenAI API latency, increase timeout settings

**Issue: Database connection errors**
- Solution: Verify Supabase credentials and network connectivity

### Debug Mode

Enable debug logging temporarily:

```bash
LOG_LEVEL=DEBUG docker-compose restart
```

## Backup and Recovery

### Database Backups

Supabase provides automatic backups. For additional safety:

1. Enable point-in-time recovery
2. Export data regularly
3. Test restore procedures

### Application State

The application is stateless - no local data to backup.

## Updates and Maintenance

### Rolling Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Verify health
curl http://localhost:8000/health
```

### Zero-Downtime Deployment

Use blue-green deployment or rolling updates with a load balancer.

