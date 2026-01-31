#!/bin/bash

# Type checking script
# Runs mypy for static type analysis

set -e

echo "🔍 Running type checks..."
echo ""

# Run mypy
echo "▶ Running mypy..."
uv run mypy backend/ main.py

echo ""
echo "✅ Type checking complete!"
