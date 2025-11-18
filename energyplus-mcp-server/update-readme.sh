#!/bin/bash
# Interactive README Customization Script

echo "📝 README.md Customization"
echo "=========================="
echo ""

# Check if README.md exists
if [ ! -f "README.md" ]; then
    echo "❌ README.md not found!"
    exit 1
fi

# Backup original
cp README.md README.md.backup
echo "✅ Backed up original to README.md.backup"
echo ""

# Collect information
echo "Let's customize your README.md"
echo "Press Enter to keep current value"
echo ""

# 1. Live Demo URL
echo "1. Live Demo URL"
echo "   Current: https://YOUR_USERNAME.github.io/bayesian-energy-calibration/"
read -p "   Enter your Vercel URL (or GitHub Pages URL): " demo_url
if [ -n "$demo_url" ]; then
    sed -i "s|https://YOUR_USERNAME.github.io/bayesian-energy-calibration/bayesian_calibration_results/|$demo_url|g" README.md
    echo "   ✅ Updated demo URL"
fi
echo ""

# 2. GitHub Username
echo "2. GitHub Username"
read -p "   Enter your GitHub username: " github_user
if [ -n "$github_user" ]; then
    sed -i "s/YOUR_USERNAME/$github_user/g" README.md
    echo "   ✅ Updated GitHub username"
fi
echo ""

# 3. Email
echo "3. Contact Email"
echo "   Current: your-email@example.com"
read -p "   Enter your email: " email
if [ -n "$email" ]; then
    sed -i "s/your-email@example.com/$email/g" README.md
    echo "   ✅ Updated email"
fi
echo ""

# 4. Name for License (optional)
echo "4. Your Name (for copyright)"
read -p "   Enter your full name: " author_name
echo ""

# Create LICENSE file if name provided
if [ -n "$author_name" ]; then
    echo "5. Create LICENSE file?"
    read -p "   Create MIT License? (y/N): " create_license

    if [[ $create_license =~ ^[Yy]$ ]]; then
        cat > LICENSE << EOF
MIT License

Copyright (c) $(date +%Y) $author_name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
        echo "   ✅ Created LICENSE file"
    fi
fi
echo ""

# 5. Add LinkedIn (optional)
echo "6. LinkedIn Profile (optional)"
read -p "   Enter LinkedIn URL (or press Enter to skip): " linkedin_url

if [ -n "$linkedin_url" ]; then
    # Add LinkedIn to contact section
    sed -i "/^- Email:/a - LinkedIn: $linkedin_url" README.md
    echo "   ✅ Added LinkedIn"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ README.md Updated!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary of changes:"
[ -n "$demo_url" ] && echo "  ✅ Live demo URL: $demo_url"
[ -n "$github_user" ] && echo "  ✅ GitHub username: $github_user"
[ -n "$email" ] && echo "  ✅ Email: $email"
[ -n "$author_name" ] && echo "  ✅ Author: $author_name"
[ -n "$linkedin_url" ] && echo "  ✅ LinkedIn: $linkedin_url"
echo ""
echo "Files created/updated:"
echo "  📄 README.md (customized)"
echo "  💾 README.md.backup (original)"
[ -f LICENSE ] && echo "  📜 LICENSE (MIT)"
echo ""
echo "Next steps:"
echo "  1. Review README.md to make sure it looks good"
echo "  2. Commit changes: git add README.md LICENSE && git commit -m 'Customize README'"
echo "  3. Push to GitHub: git push"
echo ""
echo "Preview your README:"
echo "  cat README.md | head -50"
echo ""
