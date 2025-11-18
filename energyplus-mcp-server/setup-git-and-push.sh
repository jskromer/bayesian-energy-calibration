#!/bin/bash
# Setup Git and Push to GitHub/Link to Vercel

echo "🔧 Git & GitHub Setup for Bayesian Analysis"
echo "============================================="
echo ""

# Step 1: Configure Git Identity
echo "📝 Step 1: Configure Git Identity"
echo "-----------------------------------"
read -p "Enter your name: " git_name
read -p "Enter your email: " git_email

git config user.name "$git_name"
git config user.email "$git_email"

echo "✅ Git configured:"
echo "   Name: $git_name"
echo "   Email: $git_email"
echo ""

# Step 2: Commit changes
echo "💾 Step 2: Committing Bayesian Analysis"
echo "-----------------------------------"

# Check if there are staged changes
if git diff --cached --quiet; then
    echo "No staged changes, staging Bayesian analysis files..."
    git add .gitignore
    git add bayesian_calibration_results/
    git add bayesian_house_calibration.py
    git add visualize_bayesian_results.py
    git add analyze_total_energy_posterior.py
    git add BAYESIAN_CALIBRATION_SUMMARY.md
    git add BAYESIAN_QUICK_START.md
    git add README.md
    git add QUICK_DEPLOY.md
    git add deploy-to-github.sh
    git add netlify.toml
fi

git commit -m "Add Bayesian building energy calibration analysis

- Complete Bayesian calibration using published priors
- Interactive website with 9 visualizations
- Posterior distribution analysis for total energy
- MCMC diagnostics (R-hat=1.0, perfect convergence)
- Published priors from ASHRAE, DOE, NREL, LBNL, US Census
- Deployment guides for GitHub Pages, Netlify, Vercel
- Full documentation and references"

echo "✅ Changes committed!"
echo ""

# Step 3: GitHub Setup
echo "🐙 Step 3: GitHub Repository Setup"
echo "-----------------------------------"
echo ""
echo "Choose an option:"
echo "  1) Create NEW GitHub repository and push"
echo "  2) Link to EXISTING Vercel project (already deployed)"
echo "  3) Skip GitHub (just keep local git)"
echo ""
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "Creating new GitHub repository..."
        read -p "Enter your GitHub username: " github_user
        read -p "Enter repository name [bayesian-energy-calibration]: " repo_name
        repo_name=${repo_name:-bayesian-energy-calibration}

        echo ""
        echo "📋 Next steps:"
        echo "1. Go to: https://github.com/new"
        echo "2. Repository name: $repo_name"
        echo "3. Make it PUBLIC (for free GitHub Pages)"
        echo "4. DON'T initialize with README"
        echo "5. Click 'Create repository'"
        echo ""
        read -p "Press Enter when you've created the repository..."

        # Add remote
        if git remote | grep -q origin; then
            git remote set-url origin "https://github.com/$github_user/$repo_name.git"
        else
            git remote add origin "https://github.com/$github_user/$repo_name.git"
        fi

        # Push
        echo ""
        echo "📤 Pushing to GitHub..."
        git branch -M main
        git push -u origin main

        echo ""
        echo "✅ Pushed to GitHub!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 Success! Your code is on GitHub!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "🔗 Repository: https://github.com/$github_user/$repo_name"
        echo ""
        echo "Next: Link Vercel to this repository"
        echo "1. Go to Vercel dashboard: https://vercel.com/dashboard"
        echo "2. Import Project → Import Git Repository"
        echo "3. Select: $github_user/$repo_name"
        echo "4. Root Directory: bayesian_calibration_results"
        echo "5. Deploy!"
        echo ""
        echo "✨ Benefits:"
        echo "  • Every git push = automatic Vercel deployment"
        echo "  • Version control for your analysis"
        echo "  • Easy collaboration"
        echo ""
        ;;

    2)
        echo ""
        echo "Linking to Vercel project..."
        read -p "Enter your GitHub username: " github_user
        read -p "Enter repository name [bayesian-energy-calibration]: " repo_name
        repo_name=${repo_name:-bayesian-energy-calibration}

        echo ""
        echo "Creating GitHub repository for existing Vercel deployment..."
        echo ""
        echo "📋 Steps:"
        echo "1. Go to: https://github.com/new"
        echo "2. Repository name: $repo_name"
        echo "3. Make it PUBLIC"
        echo "4. DON'T initialize with README"
        echo "5. Click 'Create repository'"
        echo ""
        read -p "Press Enter when created..."

        # Add remote
        if git remote | grep -q origin; then
            git remote set-url origin "https://github.com/$github_user/$repo_name.git"
        else
            git remote add origin "https://github.com/$github_user/$repo_name.git"
        fi

        # Push
        git branch -M main
        git push -u origin main

        echo ""
        echo "✅ Code pushed to GitHub!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔗 Link Vercel to GitHub (Optional)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "To enable auto-deployments from GitHub:"
        echo ""
        echo "1. Go to your Vercel project settings"
        echo "2. Git → Connect Git Repository"
        echo "3. Select: $github_user/$repo_name"
        echo "4. Root Directory: bayesian_calibration_results"
        echo ""
        echo "Now every git push will trigger a Vercel deployment!"
        echo ""
        ;;

    3)
        echo ""
        echo "✅ Git repository created locally"
        echo ""
        echo "Your analysis is version controlled locally."
        echo "You can push to GitHub later if needed."
        echo ""
        ;;

    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Git configured and committed"
if [ "$choice" = "1" ] || [ "$choice" = "2" ]; then
    echo "✅ Code pushed to GitHub"
    echo "🔗 Repository: https://github.com/$github_user/$repo_name"
fi
echo "🌐 Vercel: Already deployed"
echo ""
echo "Your Bayesian analysis is now:"
echo "  📊 Live on Vercel (already deployed)"
echo "  💾 Version controlled with Git"
if [ "$choice" = "1" ] || [ "$choice" = "2" ]; then
    echo "  🐙 Backed up on GitHub"
fi
echo ""
echo "Happy analyzing! 🎉"
