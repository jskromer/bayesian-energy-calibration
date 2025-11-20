# Deploying to Streamlit Cloud

This guide will help you deploy your Bayesian Energy Calibration app to Streamlit Cloud for public access.

## Prerequisites

- ✅ GitHub repository (you already have this)
- ✅ `streamlit_app.py` file (ready)
- ✅ `requirements.txt` file (configured)
- ✅ `packages.txt` file (system dependencies configured)
- ✅ `.streamlit/config.toml` file (app configuration ready)

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

Your code is already on branch `claude/utility-data-upload-01HazMgYns1p63AADYcHuCaN`.

**Option A:** If you want to deploy from this branch directly, proceed to step 2.

**Option B:** If you want to merge to main first:
```bash
# Switch to main branch
git checkout main

# Merge your feature branch
git merge claude/utility-data-upload-01HazMgYns1p63AADYcHuCaN

# Push to main
git push origin main
```

### 2. Sign Up for Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"Sign up with GitHub"**
3. Authorize Streamlit to access your GitHub repositories

### 3. Deploy Your App

1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository:** `jskromer/bayesian-energy-calibration`
   - **Branch:** `claude/utility-data-upload-01HazMgYns1p63AADYcHuCaN` (or `main` if you merged)
   - **Main file path:** `streamlit_app.py`

3. Click **"Advanced settings"** (optional):
   - **Python version:** 3.11 (recommended)
   - **Secrets:** None needed for this app

4. Click **"Deploy!"**

### 4. Wait for Deployment

- Initial deployment takes 3-5 minutes
- Streamlit Cloud will:
  - Install system packages from `packages.txt`
  - Install Python packages from `requirements.txt`
  - Start your app

### 5. Access Your App

Once deployed, you'll get a public URL like:
```
https://jskromer-bayesian-energy-calibration-streamlit-app-<hash>.streamlit.app
```

You can share this URL with anyone!

## App Settings & Management

### Custom Domain (Optional)

In the Streamlit Cloud dashboard:
1. Go to your app settings
2. Under "General" → "App URL"
3. Customize the subdomain or add a custom domain

### Monitoring

- **Logs:** View real-time logs in the Streamlit Cloud dashboard
- **Analytics:** See app usage statistics
- **Resource limits:** Free tier includes:
  - 1 GB RAM
  - 1 CPU
  - Unlimited public apps

### Updating Your App

Any push to the deployed branch will automatically trigger a redeployment:

```bash
# Make changes to your code
git add .
git commit -m "Update app"
git push origin claude/utility-data-upload-01HazMgYns1p63AADYcHuCaN

# Streamlit Cloud will auto-redeploy in ~1-2 minutes
```

## Troubleshooting

### Deployment Fails

**Check the logs** in Streamlit Cloud dashboard for error details.

Common issues:
- **Package installation fails:** Check `requirements.txt` versions
- **Out of memory:** PyMC can be memory-intensive; consider optimizing MCMC settings
- **Import errors:** Ensure all dependencies are in `requirements.txt`

### App is Slow

- **MCMC sampling is computationally expensive**
- Free tier has limited resources (1 GB RAM, 1 CPU)
- Consider:
  - Reducing default number of samples/chains
  - Adding caching with `@st.cache_data`
  - Showing progress indicators for long operations

### File Upload Not Working

- Verify `.streamlit/config.toml` has `maxUploadSize = 5` (5 MB limit)
- CSV files should be small (<1 MB for 12 months of data)

## Local Development

Test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app.py

# Access at http://localhost:8501
```

## Cost Considerations

- **Free tier:** Unlimited public apps, shared resources
- **Paid tiers:** For private apps or more resources
  - See [pricing](https://streamlit.io/cloud) for details

## Security Notes

- App is **public** by default on free tier
- Don't commit sensitive data (API keys, credentials)
- CSV uploads are processed in-memory (not stored)
- Use Streamlit secrets for any sensitive configuration

## Next Steps

1. Deploy to Streamlit Cloud following steps above
2. Test the deployment with `test_utility_data.csv`
3. Share the public URL with users
4. Monitor logs for any issues

---

**Quick Deploy Link:** [share.streamlit.io](https://share.streamlit.io)
