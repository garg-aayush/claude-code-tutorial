#!/bin/bash

# Complete quality check script
# Runs linting, type checking, and tests

set -e

echo "🚀 Running complete quality checks..."
echo ""

# Run linting
./scripts/lint.sh

echo ""

# Run tests
echo "▶ Running tests..."
cd backend && uv run pytest tests/ -v

echo ""
echo "✅ All checks passed! Code is ready for commit."
