# Connect Your Vercel Deployment to GitHub

Great! You've already deployed to Vercel. Now let's add GitHub for version control and automatic deployments.

## Why Add GitHub?

- ✅ **Version Control**: Track changes to your analysis
- ✅ **Auto-Deploy**: Every git push updates Vercel automatically
- ✅ **Backup**: Your code is safely stored on GitHub
- ✅ **Collaboration**: Easy to share and collaborate
- ✅ **Portfolio**: Showcase your work on your GitHub profile

## Quick Setup (2 Options)

### Option 1: Automated Script (Easiest)

```bash
./setup-git-and-push.sh
```

This script will:
1. Ask for your name and email (for git)
2. Commit your Bayesian analysis
3. Guide you through creating a GitHub repository
4. Push your code to GitHub
5. Show you how to link Vercel to GitHub

### Option 2: Manual Setup

#### Step 1: Configure Git

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### Step 2: Commit Your Analysis

```bash
# Add files
git add .gitignore bayesian_calibration_results/ *.py *.md *.sh netlify.toml

# Commit
git commit -m "Add Bayesian building energy calibration analysis"
```

#### Step 3: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `bayesian-energy-calibration` (or your choice)
3. Make it **PUBLIC** (required for free GitHub Pages)
4. **DON'T** check "Initialize with README"
5. Click **Create repository**

#### Step 4: Push to GitHub

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/bayesian-energy-calibration.git

# Push
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub credentials.

#### Step 5: Link Vercel to GitHub (Optional but Recommended)

This enables automatic deployments when you push to GitHub:

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Find your Bayesian analysis project
3. Click **Settings** → **Git**
4. Click **Connect Git Repository**
5. Select: `YOUR_USERNAME/bayesian-energy-calibration`
6. Root Directory: `bayesian_calibration_results`
7. Click **Connect**

**Now every `git push` will automatically update your Vercel site!** 🚀

## Workflow After Setup

### Make Updates

```bash
# Edit your files
# ...

# Stage changes
git add .

# Commit
git commit -m "Update analysis with new data"

# Push to GitHub (triggers automatic Vercel deployment)
git push
```

Vercel will automatically:
- Detect the push
- Build and deploy your site
- Update your live URL

### Check Deployment Status

Visit: https://vercel.com/dashboard

You'll see:
- ✅ Latest deployment status
- 📊 Build logs
- 🌐 Live URL
- 📈 Analytics (if enabled)

## Benefits of This Setup

### Before (Vercel Only)
- ❌ No version history
- ❌ Manual deployments via CLI
- ❌ No backup
- ❌ Hard to collaborate

### After (Vercel + GitHub)
- ✅ Full version history
- ✅ Automatic deployments
- ✅ Backed up on GitHub
- ✅ Easy collaboration
- ✅ Track changes over time
- ✅ Revert to previous versions if needed

## Your Current Setup

### Vercel
- ✅ **Already deployed**
- 🌐 **Live URL**: (your Vercel URL)
- 📊 **Website**: Interactive Bayesian analysis

### GitHub (After Setup)
- 💾 **Repository**: Version control
- 🔄 **Auto-sync**: Pushes trigger Vercel deployments
- 📁 **Backup**: All code safely stored

## Troubleshooting

### Git Credentials

If you're prompted for username/password but it fails:

1. **Use a Personal Access Token** instead of password:
   - Go to: https://github.com/settings/tokens
   - Click **Generate new token** (classic)
   - Select scope: `repo`
   - Copy the token
   - Use as password when pushing

### Already Have a Repository?

If you already have a GitHub repo:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Vercel Not Auto-Deploying?

Make sure:
1. Vercel is connected to your GitHub repo
2. Root directory is set to: `bayesian_calibration_results`
3. Branch is set to: `main`

## Next Steps

1. **Run the setup script**:
   ```bash
   ./setup-git-and-push.sh
   ```

2. **Make your first update**:
   - Edit a file (e.g., update README.md)
   - Commit and push
   - Watch Vercel auto-deploy!

3. **Share your work**:
   - GitHub URL: Share your code
   - Vercel URL: Share your live website

## Questions?

- **Script issues**: Check that it's executable: `chmod +x setup-git-and-push.sh`
- **Git questions**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Vercel questions**: https://vercel.com/docs

---

**Ready to connect your Vercel deployment to GitHub?**

```bash
./setup-git-and-push.sh
```

🚀 Let's go!
