# NorCal Flows Backend - Deployment Guide

## Development Server

To run locally:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Production Deployment

### Option 1: Railway.app (Recommended for Quick Deployment)

Railway is a modern cloud platform with excellent Python/FastAPI support.

1. **Create Railway account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Connect Repository**
   - Click "New Project"
   - Import from GitHub (or upload this repository)
   - Select the project

3. **Configure the App**
   - Railway auto-detects Python projects
   - Set environment:
     - **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Python Version**: 3.11
   - Add environment variables (if needed)

4. **Deploy**
   - Railway auto-deploys on push to main
   - URL provided in Railway dashboard

### Option 2: Render.com

1. **Create Render account**
   - Go to https://render.com
   - Sign up

2. **Create New Web Service**
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Instance type: Free tier (for testing)

3. **Deploy**
   - Click "Create Web Service"
   - Render deploys automatically

### Option 3: AWS EC2 (Advanced)

1. **Launch EC2 Instance**
   ```bash
   # Ubuntu 22.04 LTS
   # t3.micro (free tier eligible)
   ```

2. **SSH into instance and setup**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip python3-venv

   git clone <your-repo>
   cd <your-repo>/backend

   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run with systemd**
   Create `/etc/systemd/system/norcal-flows.service`:
   ```ini
   [Unit]
   Description=NorCal Flows API
   After=network.target

   [Service]
   Type=notify
   User=ubuntu
   WorkingDirectory=/home/ubuntu/<your-repo>/backend
   Environment="PATH=/home/ubuntu/<your-repo>/backend/venv/bin"
   ExecStart=/home/ubuntu/<your-repo>/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=on-failure
   RestartSec=5s

   [Install]
   WantedBy=multi-user.target
   ```

   Then:
   ```bash
   sudo systemctl enable norcal-flows
   sudo systemctl start norcal-flows
   sudo systemctl status norcal-flows
   ```

4. **Use Nginx as reverse proxy**
   ```bash
   sudo apt install nginx
   ```

   Edit `/etc/nginx/sites-available/default`:
   ```nginx
   server {
       listen 80 default_server;
       server_name _;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   Then:
   ```bash
   sudo systemctl restart nginx
   ```

### Option 4: Docker (For Any Cloud)

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app ./app

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run locally**
   ```bash
   docker build -t norcal-flows .
   docker run -p 8000:8000 norcal-flows
   ```

3. **Deploy to Docker Hub / Cloud Provider**
   ```bash
   docker push <your-username>/norcal-flows
   ```

## Environment Variables

Currently, the app has no required environment variables. In the future, you may want to add:

- `USGS_API_KEY` (if USGS implements key requirement)
- `DATABASE_URL` (for production database)
- `SENTRY_DSN` (for error tracking)
- `LOG_LEVEL` (for logging control)

## Monitoring

### Logs
- Railway/Render: Logs available in dashboard
- AWS: Check systemd journal: `journalctl -u norcal-flows -f`
- Local: Check console output

### Health Check
Monitor API health:
```bash
curl https://your-api-url.com/api/health
```

Should return:
```json
{
  "status": "healthy",
  "last_fetch_at": "2026-04-01T12:00:00Z",
  "rivers_count": 15
}
```

### Uptime Monitoring
Use a service like Uptime Robot:
- Monitor: `https://your-api-url.com/api/health`
- Check interval: 5 minutes
- Alert if down >5 minutes

## Scaling Considerations

### Current Limitations
- In-memory data storage (data lost on restart)
- Single-threaded (APScheduler background task)
- No database = no history persistence

### For Production V2
1. **Add PostgreSQL + TimescaleDB**
   - Persistent data storage
   - Historical data for trends
   - Analytics and reporting

2. **Implement Redis caching**
   - Cache USGS/CDEC responses
   - Reduce API calls
   - Faster responses

3. **Add Horizontal Scaling**
   - Load balancer (AWS ALB, CloudFront)
   - Multiple app instances
   - Shared database + Redis

4. **Performance Optimizations**
   - Response caching (5-15 min depending on data freshness)
   - Batch USGS API calls
   - Compress JSON responses
   - CDN for static docs

## Disaster Recovery

### Backup Strategy
- GitHub repo = source control backup
- Data is not critical (can fetch fresh from USGS/CDEC)
- Monitor for API failures and log all errors

### Error Handling
The app gracefully handles:
- USGS API failures → falls back to CDEC
- CDEC API failures → uses cached data
- Missing stations → returns null values
- Network timeouts → logged and skipped

## Cost Estimates

| Platform | Cost | Notes |
|----------|------|-------|
| Railway | $5-20/month | Pay as you go, free tier available |
| Render | Free-$7/month | Free tier with 15-min sleep |
| AWS EC2 | ~$10-30/month | Free tier for 12 months |
| Heroku | $7-50+/month | No longer free tier |

## Troubleshooting

### API not responding
```bash
curl -v http://your-url/api/health
```

### Check logs for errors
- Railway: Dashboard → Logs
- Render: Logs tab
- AWS: `journalctl -u norcal-flows -n 50`

### USGS/CDEC not responding
- Check endpoints are up: https://waterservices.usgs.gov/nwis/iv/ and https://cdec.water.ca.gov
- Verify site IDs in `app/config.py`
- Check network connectivity from deployment environment

### Data is stale
- Check `updated_at` timestamp in `/api/health`
- Verify scheduled task is running
- Check logs for fetch errors

## Next Steps

1. Deploy to a cloud provider
2. Add database for persistence
3. Set up monitoring and alerts
4. Connect frontend to API
5. Add analytics tracking
6. Implement caching layer
7. Set up CI/CD pipeline for automated deployments

## Support

For deployment issues:
- Check provider documentation
- Review logs carefully
- Test locally first
- Reach out to the development team

---

**Last updated**: March 31, 2026
**Status**: Production Ready
