# Loud Curator - Deployment Guide

This guide covers deploying the Loud Curator application in various environments, from local development to production.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite (included with Python)
- Git

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd loud-curator-osa

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start development servers
cd ..
./start_dev.sh
```

## 🐳 Docker Deployment

### Docker Compose Setup
Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEWSDATA_API_KEY=${NEWSDATA_API_KEY}
      - GROUNDNEWS_API_KEY=${GROUNDNEWS_API_KEY}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### Backend Dockerfile
Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and logs directories
RUN mkdir -p data logs

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Create ECR Repository**:
```bash
aws ecr create-repository --repository-name loud-curator
```

2. **Build and Push Images**:
```bash
# Backend
docker build -t loud-curator-backend ./backend
docker tag loud-curator-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/loud-curator:backend
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/loud-curator:backend

# Frontend
docker build -t loud-curator-frontend ./frontend
docker tag loud-curator-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/loud-curator:frontend
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/loud-curator:frontend
```

3. **Create ECS Task Definition**:
```json
{
  "family": "loud-curator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/loud-curator:backend",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "${OPENAI_API_KEY}"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/loud-curator",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Using AWS Lambda (Serverless)

1. **Create Lambda Function**:
```bash
# Package the application
pip install -r requirements.txt -t package/
cp -r backend/* package/

# Create deployment package
cd package
zip -r ../loud-curator-lambda.zip .
```

2. **Deploy with SAM**:
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  LoudCuratorFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: main.handler
      Runtime: python3.11
      Timeout: 30
      Environment:
        Variables:
          OPENAI_API_KEY: !Ref OpenAIApiKey
          NEWSDATA_API_KEY: !Ref NewsDataApiKey
```

### Google Cloud Platform

#### Using Google Cloud Run

1. **Build and Deploy**:
```bash
# Build container
gcloud builds submit --tag gcr.io/<project-id>/loud-curator

# Deploy to Cloud Run
gcloud run deploy loud-curator \
  --image gcr.io/<project-id>/loud-curator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=<your-key>
```

### Azure

#### Using Azure Container Instances

1. **Deploy with Azure CLI**:
```bash
# Create resource group
az group create --name loud-curator-rg --location eastus

# Deploy container
az container create \
  --resource-group loud-curator-rg \
  --name loud-curator \
  --image <your-registry>/loud-curator:latest \
  --dns-name-label loud-curator \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=<your-key>
```

## 🔧 Production Configuration

### Environment Variables
Create a `.env` file for production:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
NEWSDATA_API_KEY=your_newsdata_api_key
GROUNDNEWS_API_KEY=your_groundnews_api_key

# Slack Integration
SLACK_WEBHOOK_URL=your_slack_webhook_url
SLACK_WEBHOOK_FIGMA_URL=your_figma_slack_webhook_url

# Database
DATABASE_URL=sqlite:///./data/news.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log

# Security
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=https://yourdomain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

### Nginx Configuration
Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
        }
    }
}
```

### SSL Certificate Setup

#### Using Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### Application Monitoring
- **Health Checks**: `/health` endpoint for load balancer health checks
- **Metrics**: Prometheus metrics available at `/metrics`
- **Logging**: Structured JSON logging to files and stdout

### Database Monitoring
```bash
# Check database size
sqlite3 data/news.db "SELECT COUNT(*) FROM articles;"

# Monitor performance
sqlite3 data/news.db "PRAGMA table_info(articles);"
```

### Backup Strategy
```bash
# Database backup
sqlite3 data/news.db ".backup backup/news_$(date +%Y%m%d_%H%M%S).db"

# Log rotation
logrotate /etc/logrotate.d/loud-curator
```

## 🔒 Security Considerations

### API Key Management
- Use environment variables for sensitive data
- Rotate API keys regularly
- Use AWS Secrets Manager or similar for production

### Network Security
- Enable HTTPS only
- Configure CORS properly
- Use WAF for additional protection

### Application Security
- Keep dependencies updated
- Run security scans regularly
- Implement rate limiting

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**:
```bash
# Check database file permissions
ls -la data/news.db

# Repair corrupted database
sqlite3 data/news.db "PRAGMA integrity_check;"
```

2. **API Key Issues**:
```bash
# Test API connections
curl -X POST http://localhost:8000/api/settings/test-connection
```

3. **Memory Issues**:
```bash
# Monitor memory usage
ps aux | grep uvicorn
free -h
```

### Log Analysis
```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# Monitor API calls
grep "API call" logs/requests.log
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancers for multiple instances
- Implement database connection pooling
- Use Redis for session storage

### Vertical Scaling
- Increase CPU and memory allocation
- Optimize database queries
- Implement caching strategies

### Performance Optimization
- Enable gzip compression
- Use CDN for static assets
- Implement database indexing

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker images
        run: |
          docker build -t loud-curator:${{ github.sha }} .
          docker push loud-curator:${{ github.sha }}
      
      - name: Deploy to production
        run: |
          # Deploy to your cloud provider
          echo "Deploying to production..."
```

## 📞 Support

For deployment issues:
1. Check the logs in the `logs/` directory
2. Review the troubleshooting section
3. Open an issue on GitHub with detailed error information
4. Include system information and deployment environment details 