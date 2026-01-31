#!/bin/bash

# Linting script
# Runs all linting and type checking tools

set -e

echo "🔍 Running code quality checks..."
echo ""

# Check formatting with black
echo "▶ Checking code formatting (black)..."
uv run black --check backend/ main.py

# Check import sorting with isort
echo "▶ Checking import sorting (isort)..."
uv run isort --check-only backend/ main.py

# Run flake8
echo "▶ Running flake8..."
uv run flake8 backend/ main.py

# Run mypy (optional - can be disabled if type annotations are incomplete)
# Uncomment the lines below to enable strict type checking:
# echo "▶ Running type checks (mypy)..."
# uv run mypy backend/ main.py

echo ""
echo "✅ All quality checks passed!"
