#!/bin/bash
# Automated GitHub Pages Deployment Script
# For Bayesian Building Energy Calibration Analysis

set -e  # Exit on error

echo "🚀 Bayesian Analysis - GitHub Pages Deployment"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "bayesian_calibration_results" ]; then
    echo "❌ Error: bayesian_calibration_results directory not found"
    echo "Please run this script from /workspace/energyplus-mcp-server"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env

# EnergyPlus output (keep results, ignore temp files)
*.audit
*.bnd
*.dxf
*.eio
*.end
*.err
*.eso
*.mdd
*.mtd
*.mtr
*.rdd
*.shd
*.svg
Energy+.ini

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Large files (keep only the analysis results)
*.epw
*.idf
# But keep the specific files we want
!bayesian_calibration_results/**
EOF
    echo "✅ .gitignore created"
fi

# Add files
echo ""
echo "📁 Adding files to git..."
git add bayesian_calibration_results/
git add *.py 2>/dev/null || true
git add *.md 2>/dev/null || true
git add .gitignore
echo "✅ Files added"

# Get commit message
echo ""
read -p "📝 Enter commit message (or press Enter for default): " commit_msg
commit_msg=${commit_msg:-"Update Bayesian building energy calibration analysis"}

# Commit
echo "💾 Committing changes..."
git commit -m "$commit_msg" || {
    echo "ℹ️  No changes to commit (everything up to date)"
}

# Get GitHub credentials
echo ""
echo "🔐 GitHub Repository Configuration"
echo "-----------------------------------"
read -p "Enter your GitHub username: " github_user

if [ -z "$github_user" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

read -p "Enter repository name [bayesian-energy-calibration]: " repo_name
repo_name=${repo_name:-bayesian-energy-calibration}

# Check if remote exists
if git remote | grep -q origin; then
    current_remote=$(git remote get-url origin)
    echo ""
    echo "ℹ️  Remote 'origin' already exists: $current_remote"
    read -p "Do you want to update it? (y/N): " update_remote
    if [[ $update_remote =~ ^[Yy]$ ]]; then
        git remote set-url origin "https://github.com/$github_user/$repo_name.git"
        echo "✅ Remote updated"
    fi
else
    git remote add origin "https://github.com/$github_user/$repo_name.git"
    echo "✅ Remote added"
fi

# Rename branch to main if needed
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "🔄 Renaming branch to 'main'..."
    git branch -M main
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
echo "-----------------------------------"
echo "ℹ️  You may be prompted for your GitHub credentials"
echo ""

if git push -u origin main; then
    echo ""
    echo "✅ Successfully deployed to GitHub!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Next Steps:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Go to: https://github.com/$github_user/$repo_name"
    echo ""
    echo "2. Enable GitHub Pages:"
    echo "   • Click 'Settings' → 'Pages'"
    echo "   • Source: Deploy from a branch"
    echo "   • Branch: main → / (root)"
    echo "   • Click 'Save'"
    echo ""
    echo "3. Your site will be live at:"
    echo "   🌐 https://$github_user.github.io/$repo_name/bayesian_calibration_results/"
    echo ""
    echo "4. (Optional) For a cleaner URL, you can:"
    echo "   • Move bayesian_calibration_results/* to root"
    echo "   • Then access at: https://$github_user.github.io/$repo_name/"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📚 Documentation: see DEPLOYMENT_GUIDE.md"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo ""
    echo "1. Repository doesn't exist on GitHub:"
    echo "   → Create it at: https://github.com/new"
    echo "   → Name it: $repo_name"
    echo "   → Make it Public (for free GitHub Pages)"
    echo "   → DON'T initialize with README"
    echo "   → Then run this script again"
    echo ""
    echo "2. Authentication failed:"
    echo "   → Use a Personal Access Token instead of password"
    echo "   → Create one at: https://github.com/settings/tokens"
    echo "   → Select scope: 'repo'"
    echo ""
    echo "3. Force push (if needed):"
    echo "   git push -u origin main --force"
    echo ""
    exit 1
fi
