# Deployment Guide for Bayesian Energy Calibration

This guide covers how to deploy the Bayesian Energy Calibration project, including both the interactive Streamlit application and the static analysis results.

## Table of Contents

- [Deployment Options Overview](#deployment-options-overview)
- [Option 1: Streamlit Community Cloud (Recommended for App)](#option-1-streamlit-community-cloud-recommended-for-app)
- [Option 2: GitHub Pages (For Static Results)](#option-2-github-pages-for-static-results)
- [Option 3: Vercel (For Static Results)](#option-3-vercel-for-static-results)
- [Option 4: Docker Deployment](#option-4-docker-deployment)
- [Option 5: Cloud Platforms (AWS, GCP, Azure)](#option-5-cloud-platforms-aws-gcp-azure)
- [Custom Domain Setup](#custom-domain-setup)
- [Troubleshooting](#troubleshooting)

---

## Deployment Options Overview

| Option | Best For | Cost | Difficulty | Features |
|--------|----------|------|-----------|----------|
| **Streamlit Cloud** | Interactive app | Free | Easy | Full app functionality |
| **GitHub Pages** | Static results | Free | Easy | Simple hosting |
| **Vercel** | Static results | Free | Easy | Fast CDN, analytics |
| **Docker** | Self-hosting | Varies | Medium | Full control |
| **AWS/GCP/Azure** | Production | $10+/mo | Hard | Scalable, professional |

---

## Option 1: Streamlit Community Cloud (Recommended for App)

**Best for**: Deploying the interactive Streamlit application

### Prerequisites
- GitHub account
- This repository pushed to GitHub
- Streamlit Community Cloud account (free)

### Steps

1. **Push your code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Prepare for Streamlit deployment"
   git push origin main
   ```

2. **Sign up for Streamlit Community Cloud**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"

3. **Deploy your app**
   - Repository: Select `bayesian-energy-calibration`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
   - Click "Deploy!"

4. **Access your app**
   - URL: `https://your-username-bayesian-energy-calibration.streamlit.app`
   - App will be live in 2-3 minutes

### Configuration

Create `.streamlit/config.toml` if not present:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

### Environment Variables (if needed)

If your app uses environment variables:
1. In Streamlit Cloud dashboard, go to your app
2. Click "Settings" → "Secrets"
3. Add secrets in TOML format:
   ```toml
   # Example secrets
   API_KEY = "your-api-key"
   ```

### Pros & Cons

**Pros:**
- ✅ Free for public repos
- ✅ Easy deployment (3 clicks)
- ✅ Auto-updates on git push
- ✅ Managed infrastructure
- ✅ Built-in authentication

**Cons:**
- ❌ Public repos only (free tier)
- ❌ Resource limits on free tier
- ❌ May sleep after inactivity

---

## Option 2: GitHub Pages (For Static Results)

**Best for**: Hosting static HTML results from the analysis

### Quick Deployment

This repository is already configured for GitHub Pages deployment.

#### Automated Script

```bash
./deploy-to-github.sh
```

#### Manual Steps

1. **Ensure your repo is on GitHub**
   ```bash
   git remote -v  # Check if origin is set
   ```

2. **Enable GitHub Pages**
   - Go to your GitHub repository
   - Click **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main** → **/ (root)**
   - Click **Save**

3. **Access your site**
   - URL: `https://YOUR_USERNAME.github.io/bayesian-energy-calibration/`
   - Wait 1-2 minutes for first deployment

### Publishing Analysis Results

If you have static results in `bayesian_calibration_results/`:

```bash
# Make sure index.html exists
ls bayesian_calibration_results/index.html

# Commit and push
git add bayesian_calibration_results/
git commit -m "Add analysis results"
git push origin main
```

Your results will be at: `https://YOUR_USERNAME.github.io/bayesian-energy-calibration/bayesian_calibration_results/`

### Pros & Cons

**Pros:**
- ✅ Free
- ✅ Fast (CDN)
- ✅ Custom domains
- ✅ Free SSL
- ✅ Great for portfolios

**Cons:**
- ❌ Static content only
- ❌ No backend processing
- ❌ Public repos only

---

## Option 3: Vercel (For Static Results)

**Best for**: Modern static site hosting with analytics

### Using Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel --prod
   ```

3. **Follow prompts**
   - Login to Vercel
   - Link to existing project or create new
   - Confirm deployment

### Using GitHub Integration

1. **Go to Vercel**
   - Visit https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "New Project"
   - Import `bayesian-energy-calibration`
   - Configure:
     - Framework: None (static)
     - Root Directory: `./`
     - Build Command: (leave empty)
     - Output Directory: `bayesian_calibration_results` (if deploying results)

3. **Deploy**
   - Click "Deploy"
   - Get URL: `https://bayesian-energy-calibration.vercel.app`

### Pros & Cons

**Pros:**
- ✅ Free tier
- ✅ Very fast CDN
- ✅ Analytics included
- ✅ Auto-deploy on push
- ✅ Custom domains

**Cons:**
- ❌ Requires account
- ❌ Limited builds/month (free tier)

---

## Option 4: Docker Deployment

**Best for**: Self-hosting, reproducible deployments

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY packages.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
    restart: unless-stopped
```

### Deployment Steps

1. **Build the image**
   ```bash
   docker build -t bayesian-energy-calibration .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 bayesian-energy-calibration
   ```

   Or with docker-compose:
   ```bash
   docker-compose up -d
   ```

3. **Access the app**
   - Local: `http://localhost:8501`
   - Server: `http://your-server-ip:8501`

### Deploy to Docker Hub

```bash
# Tag the image
docker tag bayesian-energy-calibration your-username/bayesian-energy-calibration:latest

# Push to Docker Hub
docker push your-username/bayesian-energy-calibration:latest

# Pull and run on any server
docker pull your-username/bayesian-energy-calibration:latest
docker run -p 8501:8501 your-username/bayesian-energy-calibration:latest
```

---

## Option 5: Cloud Platforms (AWS, GCP, Azure)

### AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize**
   ```bash
   eb init -p docker bayesian-energy-calibration
   ```

3. **Create environment and deploy**
   ```bash
   eb create bayesian-env
   eb open
   ```

### Google Cloud Run

1. **Build and deploy**
   ```bash
   gcloud run deploy bayesian-energy-calibration \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Access**
   - URL provided after deployment
   - Example: `https://bayesian-energy-calibration-xyz.run.app`

### Azure App Service

1. **Create App Service**
   ```bash
   az webapp up --name bayesian-energy-calibration \
     --resource-group myResourceGroup \
     --runtime "PYTHON:3.11"
   ```

2. **Configure deployment**
   ```bash
   az webapp config appsettings set \
     --name bayesian-energy-calibration \
     --resource-group myResourceGroup \
     --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
   ```

### Cost Estimates

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| AWS EB | 750 hrs/mo (12 months) | $10-50/mo |
| GCP Cloud Run | 2M requests/mo | $0.01/hr after free tier |
| Azure App Service | Limited | $13+/mo |

---

## Custom Domain Setup

### For Streamlit Cloud

1. **Get custom domain** (e.g., from Namecheap, GoDaddy)

2. **In your DNS settings, add CNAME record:**
   - Name: `app` (or `www`)
   - Value: `your-app.streamlit.app`

3. **In Streamlit Cloud:**
   - Go to app settings
   - Add custom domain
   - Verify ownership

### For GitHub Pages

1. **In DNS settings, add CNAME record:**
   - Name: `www` (or subdomain)
   - Value: `your-username.github.io`

2. **In GitHub repository:**
   - Settings → Pages
   - Custom domain: `www.yourdomain.com`
   - Enable "Enforce HTTPS"

### For Vercel

1. **In DNS settings, add CNAME record:**
   - Name: `www` (or subdomain)
   - Value: `cname.vercel-dns.com`

2. **In Vercel dashboard:**
   - Project Settings → Domains
   - Add domain
   - Follow verification steps

---

## Environment Variables & Secrets

### For Streamlit Cloud

Create `.streamlit/secrets.toml` (local only, add to `.gitignore`):
```toml
# API keys and secrets
api_key = "your-secret-key"
database_url = "postgresql://..."
```

Add to Streamlit Cloud via dashboard.

### For Docker

Use environment variables in `docker-compose.yml`:
```yaml
environment:
  - API_KEY=${API_KEY}
  - DATABASE_URL=${DATABASE_URL}
```

Or use `.env` file:
```bash
API_KEY=your-secret-key
DATABASE_URL=postgresql://...
```

### For Cloud Platforms

All platforms support environment variables via CLI or web console.

---

## CI/CD Pipeline (Optional)

### GitHub Actions for Streamlit

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Streamlit

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python -m pytest tests/

      # Streamlit Cloud auto-deploys on push
      # This is just for testing before deployment
```

---

## Monitoring & Analytics

### Add Google Analytics

Add to your Streamlit app or HTML:
```python
# In streamlit_app.py
import streamlit.components.v1 as components

components.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", height=0)
```

### Application Monitoring

For production deployments, consider:
- **Sentry**: Error tracking
- **DataDog**: APM and logging
- **New Relic**: Performance monitoring

---

## Troubleshooting

### Streamlit App Won't Start

**Issue**: App shows error on Streamlit Cloud

**Solutions:**
1. Check `requirements.txt` has all dependencies
2. Verify Python version compatibility
3. Check logs in Streamlit Cloud dashboard
4. Ensure `streamlit_app.py` is at repository root

### GitHub Pages 404 Error

**Issue**: Pages show 404 after deployment

**Solutions:**
1. Ensure `index.html` exists in root or specified folder
2. Wait 2-3 minutes after enabling Pages
3. Check Settings → Pages for deployment status
4. Verify branch and folder settings are correct

### Docker Build Fails

**Issue**: Docker image won't build

**Solutions:**
1. Check Dockerfile syntax
2. Ensure all files are copied correctly
3. Verify base image is available
4. Check for port conflicts (8501)

### Memory Issues

**Issue**: App runs out of memory

**Solutions:**
1. Optimize data loading (use caching)
2. Increase container memory limits
3. Use pagination for large datasets
4. Consider upgrading hosting tier

### Slow Performance

**Issue**: App is slow to load/respond

**Solutions:**
1. Use `@st.cache_data` for expensive operations
2. Optimize Bayesian model computations
3. Pre-compute results where possible
4. Use CDN for static assets

---

## Security Best Practices

1. **Never commit secrets**
   - Add `.streamlit/secrets.toml` to `.gitignore`
   - Use environment variables for API keys

2. **Enable HTTPS**
   - All platforms provide free SSL
   - Enable "Enforce HTTPS" in settings

3. **Authentication** (if needed)
   - Streamlit Cloud has built-in auth
   - For custom auth, use `streamlit-authenticator`

4. **Rate Limiting**
   - Consider adding rate limits for public APIs
   - Use caching to reduce server load

---

## Recommended Deployment Strategy

For the Bayesian Energy Calibration project:

1. **Development**: Run locally
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Staging**: Deploy to Streamlit Cloud (free)
   - Branch: `develop` or `staging`
   - Test all features

3. **Production**: Choose based on needs
   - **Academic/Portfolio**: Streamlit Cloud (free)
   - **Professional**: AWS/GCP/Azure (paid)
   - **Static Results**: GitHub Pages (free)

---

## Getting Help

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **GitHub Pages**: https://pages.github.com/
- **Vercel Docs**: https://vercel.com/docs
- **Docker Docs**: https://docs.docker.com/

For project-specific issues, open an issue on GitHub.

---

## Next Steps

After deployment:

1. ✅ Test all functionality
2. ✅ Set up custom domain (optional)
3. ✅ Add monitoring/analytics
4. ✅ Configure CI/CD pipeline
5. ✅ Share your deployment URL!

---

**Last Updated**: 2025-11-20

**Deployment Status**: This guide is current as of the latest platform updates.
