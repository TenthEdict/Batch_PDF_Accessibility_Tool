#!/bin/bash
# Git Repository Cleanup Script
# Removes archived, development artifacts, and documentation from git tracking
# Note: Files remain on disk for local reference

set -e  # Exit on error

echo "=========================================="
echo "ePubs Git Repository Cleanup"
echo "=========================================="
echo ""
echo "This script will REMOVE from git tracking:"
echo "  1. archived/ directory (deprecated code, test outputs)"
echo "  2. docs/ directory (all documentation except root README.md)"
echo "  3. .memory-bank/ (AI context files)"
echo "  4. .clauderules (AI configuration)"
echo "  5. .claude/ (AI working directory)"
echo ""
echo "⚠️  IMPORTANT: Only root README.md will be in remote repository"
echo "    All other .md files remain on disk but won't be tracked by git"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Removing archived/ from git tracking..."
git rm -r --cached archived/ 2>/dev/null || echo "  (already untracked or doesn't exist)"

echo ""
echo "Step 2: Removing docs/ directory from git tracking..."
git rm -r --cached docs/ 2>/dev/null || echo "  (already untracked or doesn't exist)"

echo ""
echo "Step 3: Removing .memory-bank/ from git tracking..."
git rm -r --cached .memory-bank/ 2>/dev/null || echo "  (already untracked or doesn't exist)"

echo ""
echo "Step 4: Removing .clauderules from git tracking..."
git rm --cached .clauderules 2>/dev/null || echo "  (already untracked or doesn't exist)"

echo ""
echo "Step 5: Removing .claude/ from git tracking..."
git rm -r --cached .claude/ 2>/dev/null || echo "  (already untracked or doesn't exist)"

echo ""
echo "Step 6: Removing any other .md files except README.md..."
git ls-files '*.md' | grep -v '^README\.md$' | xargs -r git rm --cached 2>/dev/null || echo "  (no other .md files tracked)"

echo ""
echo "Step 7: Checking current status..."
echo ""
git status --short

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Files removed from git tracking:"
echo "  ✓ archived/ (deprecated code and outputs)"
echo "  ✓ docs/ (all local documentation)"
echo "  ✓ .memory-bank/ (AI context)"
echo "  ✓ .clauderules and .claude/ (AI config)"
echo "  ✓ All .md files except README.md"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Stage .gitignore: git add .gitignore"
echo "  3. Commit: git commit -m 'Remove documentation and archived content from tracking'"
echo "  4. Push to remote: git push"
echo ""
echo "⚠️  Remote repository will only contain:"
echo "    - Root README.md"
echo "    - Source code (processor/, scraper/, tests/, scripts/)"
echo "    - Configuration files (pyproject.toml, requirements*.txt)"
echo ""
echo "📝 All other files remain on your local disk for reference"
echo ""
