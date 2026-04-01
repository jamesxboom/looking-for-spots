# Deployment Guide

## Local Development

### First Time Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

The app will automatically:
- Fetch from `http://localhost:8000/api/rivers` (configurable)
- Auto-refresh data every 5 minutes
- Show loading states while fetching
- Display errors if backend is unavailable

## Production Build

### Build Locally

```bash
npm run build
```

This creates a `dist/` folder with:
- Minified React code
- Bundled CSS and JavaScript
- Optimized assets
- Ready for deployment

### Preview Production Build

```bash
npm run preview
```

This serves the `dist/` folder locally at `http://localhost:4173` to test the production build.

## Deployment Platforms

### Option 1: Vercel (Recommended)

Vercel is the official Vite hosting partner with instant deploys.

#### First Time

```bash
npm install -g vercel
vercel
```

Follow the prompts:
1. Link to GitHub (recommended)
2. Select project root
3. Import settings
4. Deploy

#### For Updates

```bash
git push origin main
```

Vercel automatically rebuilds and deploys on every push.

#### Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

```
VITE_API_BASE_URL=https://api.norcalflows.com
```

### Option 2: Netlify

#### First Time

```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### With Git

```bash
# Connect GitHub repo
netlify sites:create

# Set build settings:
# Build command: npm run build
# Publish directory: dist
```

#### Environment Variables

Netlify Dashboard → Settings → Build & deploy → Environment:

```
VITE_API_BASE_URL=https://api.norcalflows.com
```

### Option 3: GitHub Pages

#### Setup

In `vite.config.js`, add base path:

```javascript
export default defineConfig({
  base: '/norcal-flows/',
  // ...
})
```

#### Deploy

```bash
npm run build
git add dist/
git commit -m "Deploy to GitHub Pages"
git push origin main
```

In GitHub Settings → Pages:
- Source: Deploy from a branch
- Branch: main
- Folder: /dist

### Option 4: Docker

#### Build Image

```bash
docker build -t norcal-flows-frontend:1.0.0 .
```

#### Run Locally

```bash
docker run -p 3000:3000 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  norcal-flows-frontend:1.0.0
```

#### Push to Registry

```bash
docker tag norcal-flows-frontend:1.0.0 \
  myregistry.azurecr.io/norcal-flows-frontend:1.0.0
docker push myregistry.azurecr.io/norcal-flows-frontend:1.0.0
```

#### Deploy to Container Services

**Azure Container Instances:**
```bash
az container create \
  --resource-group mygroup \
  --name norcal-flows \
  --image myregistry.azurecr.io/norcal-flows-frontend:1.0.0 \
  --ports 3000 \
  --environment-variables VITE_API_BASE_URL=https://api.norcalflows.com
```

**Google Cloud Run:**
```bash
gcloud run deploy norcal-flows \
  --image gcr.io/myproject/norcal-flows-frontend:1.0.0 \
  --port 3000 \
  --set-env-vars VITE_API_BASE_URL=https://api.norcalflows.com
```

**AWS Elastic Container Service:**
- Create task definition with container image
- Create service pointing to task
- Set environment variables in task definition

### Option 5: Node Server (Railway, Render, etc.)

#### Railway

1. Push code to GitHub
2. Create new project on railway.app
3. Connect GitHub repo
4. Add environment variable: `VITE_API_BASE_URL=https://api.norcalflows.com`
5. Railway auto-deploys on push

#### Render

1. Connect GitHub repo
2. Create new web service
3. Build command: `npm install && npm run build`
4. Start command: `npm install -g serve && serve -s dist -l 3000`
5. Set environment variables
6. Deploy

### Option 6: Static Hosting (S3, Cloudflare Pages, Surge, etc.)

```bash
# Build
npm run build

# Upload dist/ folder to your static host
# Ensure VITE_API_BASE_URL is set correctly in .env before building
```

**AWS S3 + CloudFront:**
```bash
aws s3 sync dist/ s3://norcal-flows-bucket/
aws cloudfront create-invalidation --distribution-id E123ABC --paths "/*"
```

**Cloudflare Pages:**
1. Connect GitHub repo
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Deploy

## Environment Configuration

### Development

Create `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Production

Create `.env.production`:
```
VITE_API_BASE_URL=https://api.norcalflows.com
```

Or set in deployment platform's environment variables.

## Backend URL Configuration

The frontend connects to:
```
{VITE_API_BASE_URL}/api/rivers
{VITE_API_BASE_URL}/api/rivers/{id}
{VITE_API_BASE_URL}/api/rivers/{id}/history
```

Ensure:
1. Backend is running on specified URL
2. CORS is enabled (backend headers allow frontend domain)
3. URL is reachable from frontend domain
4. No proxy required for same-domain setups

## SSL/HTTPS

### Important

Always use HTTPS in production!

**Vercel**: Automatic SSL ✓
**Netlify**: Automatic SSL ✓
**GitHub Pages**: Automatic SSL ✓
**Docker**: Use reverse proxy (nginx/caddy)
**Node**: Use reverse proxy or SSL cert

Example nginx reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name norcalflows.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Performance Optimization

### Build Size

```bash
npm run build
# Check size
du -sh dist/
```

Typical size: ~150KB gzipped

### Caching

Add to deployment config (example for Vercel):

`vercel.json`:
```json
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### CDN Configuration

Enable CDN on your platform:
- **Vercel**: Automatic ✓
- **Netlify**: Automatic ✓
- **Cloudflare Pages**: Automatic ✓
- **AWS S3**: Add CloudFront distribution
- **GCP**: Add Cloud CDN
- **Azure**: Add Azure CDN

## Monitoring & Analytics

### Error Tracking

Add Sentry for error monitoring:

```bash
npm install @sentry/react @sentry/tracing
```

In `src/main.jsx`:
```javascript
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: "https://key@sentry.io/project",
  tracesSampleRate: 1.0,
})
```

### Analytics

Add Google Analytics or similar:

```html
<!-- In index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || []
  function gtag(){dataLayer.push(arguments)}
  gtag('js', new Date())
  gtag('config', 'GA_ID')
</script>
```

## Rollback

If deployment has issues:

### Vercel
```bash
vercel rollback
```

### Netlify
Dashboard → Deploys → Previous version → Publish

### Docker
```bash
docker run -p 3000:3000 norcal-flows-frontend:old-version
```

## Health Checks

Verify deployment is working:

```bash
# Check frontend loads
curl https://norcalflows.com

# Check API connection
curl https://norcalflows.com/api/rivers
```

## CI/CD Pipeline

### GitHub Actions Example

`.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - uses: vercel/action@main
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
```

## Cost Estimates (Monthly)

- **Vercel**: Free tier, $20+/month for high traffic
- **Netlify**: Free tier, $19+/month for builds
- **GitHub Pages**: Free ✓
- **Docker on Render**: $7+/month
- **AWS S3 + CloudFront**: $1-5/month

## Security

- ✅ Vercel: Automatic HTTPS, DDoS protection
- ✅ Netlify: Automatic HTTPS, WAF available
- ✅ GitHub Pages: Automatic HTTPS
- Add CORS headers on backend
- Use environment variables for sensitive config
- Enable CSP headers
- Regular dependency updates (`npm audit`)

## Troubleshooting

### White screen on deploy

1. Check browser console for errors
2. Verify `VITE_API_BASE_URL` is set correctly
3. Check backend is accessible from frontend domain
4. Clear browser cache

### 404 errors on navigation

1. Ensure build output includes `dist/index.html`
2. Configure server to serve `index.html` for all routes
3. Check routing configuration (Vercel/Netlify auto-configure)

### API not reachable

1. Check backend URL in environment variables
2. Verify CORS headers on backend
3. Test backend directly: `curl https://api.norcalflows.com/api/rivers`
4. Check network tab in DevTools

### Slow loading

1. Check bundle size: `npm run build`
2. Enable gzip compression
3. Enable CDN caching
4. Use Chrome DevTools Lighthouse audit

## Support

See `README.md` for full documentation.
