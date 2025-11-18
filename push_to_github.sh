#!/bin/bash
# Script to push devfoam to GitHub
# Usage: ./push_to_github.sh YOUR_GITHUB_USERNAME

if [ -z "$1" ]; then
    echo "Usage: ./push_to_github.sh YOUR_GITHUB_USERNAME"
    echo "Example: ./push_to_github.sh carolinasarneveshtair"
    exit 1
fi

USERNAME=$1
REPO_NAME="devfoam"

echo "Setting up GitHub remote..."
git remote add origin https://github.com/$USERNAME/$REPO_NAME.git 2>/dev/null || \
    git remote set-url origin https://github.com/$USERNAME/$REPO_NAME.git

echo "Ensuring main branch..."
git branch -M main

echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Done! Your repo is now on GitHub:"
echo "   https://github.com/$USERNAME/$REPO_NAME"
