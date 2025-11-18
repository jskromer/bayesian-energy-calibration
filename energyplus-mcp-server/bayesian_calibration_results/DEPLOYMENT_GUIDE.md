# How to Post Your Bayesian Analysis to the Web

## Quick Options (Easiest to Hardest)

### Option 1: GitHub Pages (Recommended - FREE & Easy)

**Best for**: Sharing with colleagues, academic purposes, portfolio

#### Steps:

1. **Create a GitHub repository**
   ```bash
   cd /workspace/energyplus-mcp-server
   git init
   git add bayesian_calibration_results/
   git commit -m "Add Bayesian calibration analysis"
   ```

2. **Push to GitHub**
   ```bash
   # Create a new repo on github.com first, then:
   git remote add origin https://github.com/YOUR_USERNAME/bayesian-energy-calibration.git
   git branch -M main
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to your repo on GitHub
   - Click **Settings** → **Pages**
   - Under "Source", select **main** branch
   - Select folder: **/ (root)** or **/bayesian_calibration_results**
   - Click **Save**

4. **Access your site**
   - URL: `https://YOUR_USERNAME.github.io/bayesian-energy-calibration/bayesian_calibration_results/`
   - Usually live in 1-2 minutes!

**Pros**: Free, fast, reliable, supports custom domains
**Cons**: Public only (unless you have GitHub Pro)

---

### Option 2: Netlify Drop (Super Easy - FREE)

**Best for**: Quick sharing, no git needed

#### Steps:

1. **Prepare a zip file**
   ```bash
   cd /workspace/energyplus-mcp-server
   zip -r bayesian-analysis.zip bayesian_calibration_results/
   ```

2. **Go to Netlify Drop**
   - Visit: https://app.netlify.com/drop
   - Drag and drop your `bayesian-analysis.zip` file
   - Get instant URL like: `https://random-name-12345.netlify.app`

3. **Optional: Custom domain**
   - Sign up for free Netlify account
   - Change site name to something meaningful
   - Add custom domain if you have one

**Pros**: Easiest option, instant deployment, free SSL
**Cons**: Random URL unless you customize it

---

### Option 3: Vercel (Easy - FREE)

**Best for**: Modern hosting with analytics

#### Steps:

1. **Install Vercel CLI** (optional)
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd /workspace/energyplus-mcp-server/bayesian_calibration_results
   vercel --prod
   ```

   Or upload via web interface at https://vercel.com

3. **Get URL**
   - Instant URL like: `https://bayesian-analysis.vercel.app`

**Pros**: Fast CDN, analytics, free SSL, custom domains
**Cons**: Requires account

---

### Option 4: Google Drive/Dropbox (Public Link)

**Best for**: Very quick sharing, no signup needed

#### Steps (Google Drive):

1. **Upload folder**
   - Upload entire `bayesian_calibration_results/` folder to Google Drive

2. **Make public**
   - Right-click folder → Share → Change to "Anyone with the link"
   - Copy link

3. **Share**
   - Send link to colleagues
   - They can view/download files

**Pros**: Very easy, no signup
**Cons**: Not a "real" website, no direct HTML rendering

---

### Option 5: AWS S3 Static Hosting (Professional)

**Best for**: Enterprise/professional use, large traffic

#### Steps:

1. **Create S3 bucket**
   ```bash
   aws s3 mb s3://bayesian-energy-analysis
   ```

2. **Upload files**
   ```bash
   cd /workspace/energyplus-mcp-server
   aws s3 sync bayesian_calibration_results/ s3://bayesian-energy-analysis/ --acl public-read
   ```

3. **Enable static hosting**
   ```bash
   aws s3 website s3://bayesian-energy-analysis/ --index-document index.html
   ```

4. **Access site**
   - URL: `http://bayesian-energy-analysis.s3-website-us-east-1.amazonaws.com`

**Pros**: Scalable, professional, reliable
**Cons**: Costs money (usually $0.50-5/month), requires AWS account

---

### Option 6: Free Hosting Services

Several free options available:

#### A. **Render.com**
   - Free tier for static sites
   - Connect GitHub repo
   - Auto-deploy on push
   - URL: `https://your-site.onrender.com`

#### B. **Cloudflare Pages**
   - Free, unlimited bandwidth
   - Connect to GitHub
   - URL: `https://bayesian-analysis.pages.dev`

#### C. **Surge.sh**
   ```bash
   npm install -g surge
   cd bayesian_calibration_results
   surge
   ```
   - Instant deployment
   - URL: `https://bayesian-analysis.surge.sh`

---

## Recommended: GitHub Pages (Detailed Setup)

Since GitHub Pages is free, reliable, and widely used in academia, here's a detailed setup:

### Step-by-Step GitHub Pages Deployment

1. **Initialize Git Repository**
   ```bash
   cd /workspace/energyplus-mcp-server
   git init
   git add .
   git commit -m "Initial commit: Bayesian energy calibration analysis"
   ```

2. **Create GitHub Repository**
   - Go to https://github.com/new
   - Name: `bayesian-energy-calibration`
   - Description: "Bayesian calibration of building energy model using published priors"
   - Make it **Public** (required for free GitHub Pages)
   - Click **Create repository**

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/bayesian-energy-calibration.git
   git branch -M main
   git push -u origin main
   ```

4. **Configure GitHub Pages**
   - In your repo, go to **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main** → **/ (root)**
   - Click **Save**

5. **Update index.html path (if needed)**

   If you want the site at the root, move files:
   ```bash
   cd /workspace/energyplus-mcp-server
   mv bayesian_calibration_results/* .
   mv bayesian_calibration_results/.[!.]* .  # Move hidden files
   rmdir bayesian_calibration_results
   git add .
   git commit -m "Move to root for GitHub Pages"
   git push
   ```

6. **Access Your Site**
   - URL: `https://YOUR_USERNAME.github.io/bayesian-energy-calibration/`
   - Wait 1-2 minutes for deployment
   - Check status in Settings → Pages

### Adding a Custom Domain (Optional)

If you have a domain like `bayesian-analysis.yourdomain.com`:

1. **In your domain registrar (GoDaddy, Namecheap, etc.)**
   - Add CNAME record:
     - Name: `bayesian-analysis` (or `www`)
     - Value: `YOUR_USERNAME.github.io`

2. **In GitHub Settings → Pages**
   - Custom domain: `bayesian-analysis.yourdomain.com`
   - Enable "Enforce HTTPS"

---

## Quick Deployment Script

I can create a script to automate GitHub Pages deployment:

```bash
#!/bin/bash
# deploy-to-github.sh

echo "🚀 Deploying Bayesian Analysis to GitHub Pages"

# Check if git repo exists
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files
echo "Adding files..."
git add .

# Commit
read -p "Enter commit message (or press enter for default): " commit_msg
commit_msg=${commit_msg:-"Update Bayesian analysis"}
git commit -m "$commit_msg"

# Get GitHub username and repo
read -p "Enter your GitHub username: " username
read -p "Enter repository name (default: bayesian-energy-calibration): " repo
repo=${repo:-bayesian-energy-calibration}

# Add remote if not exists
if ! git remote | grep -q origin; then
    git remote add origin "https://github.com/$username/$repo.git"
fi

# Push
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "✅ Deployed!"
echo "Your site will be available at:"
echo "https://$username.github.io/$repo/"
echo ""
echo "Go to https://github.com/$username/$repo/settings/pages to enable GitHub Pages"
```

---

## Sharing Options Summary

| Option | Cost | Difficulty | Best For | URL Example |
|--------|------|-----------|----------|-------------|
| **GitHub Pages** | Free | Easy | Academic, portfolio | `username.github.io/repo` |
| **Netlify Drop** | Free | Very Easy | Quick sharing | `site-name.netlify.app` |
| **Vercel** | Free | Easy | Modern apps | `project.vercel.app` |
| **Surge.sh** | Free | Very Easy | Quick deployment | `project.surge.sh` |
| **Cloudflare Pages** | Free | Easy | High traffic | `project.pages.dev` |
| **AWS S3** | ~$1/mo | Medium | Professional | Custom domain |
| **Google Drive** | Free | Very Easy | File sharing | Drive share link |

---

## My Recommendation

**For your Bayesian analysis, I recommend GitHub Pages because:**

1. ✅ **Free forever**
2. ✅ **Easy to update** (just `git push`)
3. ✅ **Professional URL**
4. ✅ **Widely used in academia**
5. ✅ **Supports custom domains**
6. ✅ **Free SSL certificate**
7. ✅ **Good for portfolio/CV**

---

## Need Help?

Want me to:
1. Create the deployment script?
2. Set up a GitHub repo configuration?
3. Create a custom domain setup guide?
4. Add Google Analytics to track visitors?
5. Create a README for the GitHub repo?

Just let me know! 🚀
