# Fix Vercel 404 Error

## Problem

After pushing to GitHub, Vercel is showing:
```
404: NOT_FOUND
Code: NOT_FOUND
```

## Why This Happened

When you first deployed to Vercel, you deployed from the `bayesian_calibration_results/` folder directly. Now that the code is on GitHub, Vercel needs to know where to find the website files.

## Solution (Choose One)

### Option 1: Update Vercel Settings (Recommended)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Find your project** → Click on it

3. **Go to Settings** → **General**

4. **Root Directory**: Set to `bayesian_calibration_results`
   - Click "Edit" next to "Root Directory"
   - Enter: `bayesian_calibration_results`
   - Click "Save"

5. **Redeploy**:
   - Go to "Deployments" tab
   - Click the three dots (•••) on latest deployment
   - Click "Redeploy"

### Option 2: Reconnect Vercel to GitHub

1. **Delete current Vercel project** (optional)

2. **Import from GitHub**:
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select: `jskromer/bayesian-energy-calibration`
   - **Configure Project**:
     - Framework Preset: Other
     - Root Directory: `bayesian_calibration_results`
     - Build Command: (leave empty)
     - Output Directory: (leave empty)
   - Click "Deploy"

### Option 3: Use Vercel CLI

```bash
cd /workspace/energyplus-mcp-server/bayesian_calibration_results
vercel --prod
```

This will redeploy from the correct directory.

## After Fix

Your site should work at your Vercel URL. The `vercel.json` file I created will help Vercel find the right directory.

## Verify Fix

1. Check that `vercel.json` exists in repository root
2. Push it to GitHub:
   ```bash
   git add vercel.json
   git commit -m "Add Vercel configuration"
   git push
   ```
3. Vercel should auto-deploy correctly now

## Quick Fix Commands

```bash
# Commit the vercel.json file
git add vercel.json FIX_VERCEL_404.md
git commit -m "Add Vercel configuration to fix 404"
git push

# Or redeploy manually from correct directory
cd bayesian_calibration_results
vercel --prod
```

## Still Having Issues?

The website files are definitely there at:
- Path: `bayesian_calibration_results/index.html`
- All working files in that folder

The issue is just Vercel looking in the wrong place. Following any of the options above will fix it!
