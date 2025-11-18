# 🚀 Quick Deployment Guide

Choose your preferred method:

## Method 1: GitHub Pages (Recommended - 5 minutes)

**Automated:**
```bash
./deploy-to-github.sh
```

**Manual:**
1. Create repo at https://github.com/new (name: `bayesian-energy-calibration`)
2. Run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/bayesian-energy-calibration.git
   git push -u origin main
   ```
3. Enable Pages: Settings → Pages → Branch: main → Save
4. Access: `https://YOUR_USERNAME.github.io/bayesian-energy-calibration/bayesian_calibration_results/`

## Method 2: Netlify Drop (Easiest - 2 minutes)

1. Create zip:
   ```bash
   cd /workspace/energyplus-mcp-server
   zip -r bayesian-analysis.zip bayesian_calibration_results/
   ```

2. Go to: https://app.netlify.com/drop

3. Drag & drop `bayesian-analysis.zip`

4. Get instant URL like: `https://bayesian-analysis-xyz.netlify.app`

## Method 3: Vercel (Fast - 3 minutes)

```bash
cd bayesian_calibration_results
npx vercel --prod
```

Get URL: `https://bayesian-analysis.vercel.app`

## Method 4: Surge (Super Quick - 1 minute)

```bash
npm install -g surge
cd bayesian_calibration_results
surge
```

Choose URL: `https://bayesian-analysis.surge.sh`

---

## Need Help?

See full guide: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Testing Locally

```bash
cd bayesian_calibration_results
python3 -m http.server 8000
# Open: http://localhost:8000
```
