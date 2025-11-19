# DevFoam Web Application Deployment Guide

This guide covers deploying the DevFoam web application for internet access.

## Table of Contents

- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)

## Local Development

### Prerequisites

```bash
# Install web dependencies
pip3 install -r requirements.txt
```

### Running Locally

**Option 1: Using the launcher (Recommended)**
```bash
./devfoam-web
```

**Option 2: Using Python module**
```bash
cd src
python3 -m devfoam.web.app
```

**Option 3: Direct execution**
```bash
python3 src/devfoam/web/app.py
```

The application will be available at:
- Local: http://localhost:5001
- Network: http://your-ip-address:5001

## Production Deployment

### Using Gunicorn (Recommended)

Gunicorn is a production-grade WSGI server for Python web applications.

#### Install Gunicorn

```bash
pip3 install gunicorn
```

#### Run with Gunicorn

```bash
cd /path/to/devfoam
gunicorn -w 4 -b 0.0.0.0:8000 --chdir src devfoam.web.app:app
```

Parameters:
- `-w 4`: Use 4 worker processes (adjust based on CPU cores)
- `-b 0.0.0.0:8000`: Bind to all interfaces on port 8000
- `--chdir src`: Change to src directory before loading app

#### Systemd Service

Create `/etc/systemd/system/devfoam-web.service`:

```ini
[Unit]
Description=DevFoam Web Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/devfoam
Environment="PATH=/path/to/devfoam/venv/bin"
ExecStart=/path/to/devfoam/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 --chdir src devfoam.web.app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable devfoam-web
sudo systemctl start devfoam-web
sudo systemctl status devfoam-web
```

### Using Nginx as Reverse Proxy

Nginx can serve static files and proxy requests to Gunicorn.

#### Install Nginx

```bash
sudo apt-get update
sudo apt-get install nginx
```

#### Configure Nginx

Create `/etc/nginx/sites-available/devfoam`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Maximum upload size
    client_max_body_size 16M;

    # Static files
    location /static {
        alias /path/to/devfoam/src/devfoam/web/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/devfoam /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Cloud Platform Deployment

### Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Create Heroku App

```bash
# Login to Heroku
heroku login

# Create app
cd /path/to/devfoam
heroku create devfoam-app

# Add buildpack
heroku buildpacks:set heroku/python
```

#### Create Procfile

Create `Procfile` in project root:
```
web: gunicorn --chdir src devfoam.web.app:app
```

#### Create runtime.txt

Create `runtime.txt` in project root:
```
python-3.11.5
```

#### Deploy

```bash
# Initialize git if needed
git init
git add .
git commit -m "Initial commit"

# Deploy
git push heroku main

# Open app
heroku open
```

#### Configuration

```bash
# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```

### AWS Elastic Beanstalk

#### Prerequisites
- AWS account
- EB CLI installed

#### Initialize EB

```bash
cd /path/to/devfoam
eb init -p python-3.11 devfoam-app
```

#### Create Environment

```bash
eb create devfoam-env
```

#### Deploy

```bash
eb deploy
```

#### Open Application

```bash
eb open
```

### Google Cloud Platform (Cloud Run)

#### Prerequisites
- Google Cloud account
- gcloud CLI installed

#### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application
COPY src/ ./src/

# Expose port
ENV PORT 8080
EXPOSE 8080

# Run application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --chdir src devfoam.web.app:app
```

#### Build and Deploy

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/devfoam-web

# Deploy to Cloud Run
gcloud run deploy devfoam-web \
  --image gcr.io/YOUR_PROJECT_ID/devfoam-web \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi
```

### DigitalOcean App Platform

#### Using Web Console

1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Connect your GitHub repository
4. Configure:
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt && pip install gunicorn`
   - **Run Command**: `gunicorn --chdir src devfoam.web.app:app`
   - **HTTP Port**: 8080

5. Deploy

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Flask configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Upload configuration
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
UPLOAD_FOLDER=/tmp

# Server configuration
HOST=0.0.0.0
PORT=5001
```

Load in application:

```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
```

### Production Settings

Update `src/devfoam/web/app.py` for production:

```python
import os

# Production configuration
if os.getenv('FLASK_ENV') == 'production':
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
```

## Security Considerations

### 1. File Upload Security

- **Validate file types**: Only allow DXF, SVG, JSON
- **Limit file size**: Maximum 16MB
- **Sanitize filenames**: Use `secure_filename()`
- **Scan uploads**: Consider malware scanning for production

### 2. Input Validation

```python
# Validate numeric inputs
feed_rate = max(10, min(500, float(data.get('feed_rate', 150))))
safety_height = max(1, min(50, float(data.get('safety_height', 10))))
```

### 3. CORS Configuration

For API access from different domains:

```python
from flask_cors import CORS

# Allow specific origins
CORS(app, resources={r"/api/*": {"origins": ["https://yourdomain.com"]}})
```

### 4. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/generate', methods=['POST'])
@limiter.limit("10 per minute")
def generate_gcode():
    # ...
```

### 5. HTTPS Only

Always use HTTPS in production. Configure SSL certificate with Let's Encrypt or cloud provider.

### 6. Security Headers

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## Monitoring and Logging

### Application Logging

```python
import logging

if os.getenv('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('devfoam.log'),
            logging.StreamHandler()
        ]
    )
```

### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'version': '1.0.0'})
```

## Performance Optimization

### 1. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/shapes/<shape_id>')
@cache.cached(timeout=300)
def get_cached_shapes(shape_id):
    # ...
```

### 2. Compression

```python
from flask_compress import Compress

Compress(app)
```

### 3. CDN for Static Files

Configure Nginx or use cloud CDN for serving static files (CSS, JS).

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :5001
# Kill process
kill -9 <PID>
```

**Permission denied:**
```bash
# Change ownership
sudo chown -R www-data:www-data /path/to/devfoam

# Set permissions
sudo chmod -R 755 /path/to/devfoam
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Logs

```bash
# Application logs
tail -f devfoam.log

# Systemd logs
sudo journalctl -u devfoam-web -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Backup and Maintenance

### Automated Backups

```bash
# Backup script
#!/bin/bash
BACKUP_DIR=/backups/devfoam
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf $BACKUP_DIR/devfoam_$DATE.tar.gz /path/to/devfoam

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete
```

### Updates

```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart devfoam-web
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/devfoam/issues
- Documentation: `docs/` directory
- Email: support@yourdomain.com
