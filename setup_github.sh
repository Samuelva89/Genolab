#!/bin/bash

# Script to prepare Genolab repository for GitHub with Render deployment configurations
# This script sets up the necessary files and prepares the repo for institutional deployment

echo "Preparing Genolab repository for GitHub..."

# Check if git is installed
if ! [ -x "$(command -v git)" ]; then
  echo 'Error: git is not installed.' >&2
  exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files to git
echo "Adding files to git..."
git add .

# Create/update .gitignore to exclude sensitive files
echo "Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Environment files (to protect sensitive data)
*.env
.env.local
.env.production

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Local configuration that shouldn't be committed
services/config/local_settings.py

# Backup files
*.bak
*.backup
backup_*.json
recover_database_data.py  # Contains recovery procedures, may have sensitive info
check_*.py  # Scripts that might contain credentials

EOF

echo "Repository preparation complete!"
echo ""
echo "Next steps:"
echo "1. Commit your changes: git commit -m 'Prepare repository for Render deployment'"
echo "2. Add your remote repository: git remote add origin <your-github-repo-url>"
echo "3. Push to GitHub: git push -u origin main"
echo ""
echo "Then proceed to deploy on Render using one of the configuration files:"
echo "- mysql_render.yaml (for MySQL deployment)"
echo "- postgres_postgrest_render.yaml (for PostgreSQL + PostgREST deployment)"