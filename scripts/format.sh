#!/bin/bash

# Code formatting script
# Formats all Python code using black and isort

set -e

echo "🎨 Running code formatters..."
echo ""

# Format with black
echo "▶ Running black..."
uv run black backend/ main.py

# Sort imports with isort
echo "▶ Running isort..."
uv run isort backend/ main.py

echo ""
echo "✅ Code formatting complete!"
