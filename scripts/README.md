# Development Scripts

This directory contains scripts for maintaining code quality throughout the project.

## Available Scripts

### `format.sh` - Code Formatting
Automatically formats all Python code using black and isort.

```bash
./scripts/format.sh
```

**What it does:**
- Formats code with black (line length: 88)
- Sorts imports with isort (compatible with black)
- Modifies files in-place

**When to use:**
- Before committing code
- After writing new features
- To ensure consistent formatting across the codebase

### `lint.sh` - Code Quality Checks
Runs linting and type checking without modifying files.

```bash
./scripts/lint.sh
```

**What it checks:**
- Black formatting (--check mode)
- Import sorting with isort (--check-only mode)
- PEP 8 style guide compliance with flake8
- Type hints with mypy

**When to use:**
- Before committing to verify code quality
- In CI/CD pipelines
- To identify issues without auto-fixing

### `check.sh` - Complete Quality Check
Runs all quality checks plus tests.

```bash
./scripts/check.sh
```

**What it does:**
1. Runs all linting checks (lint.sh)
2. Runs the full test suite with pytest
3. Reports overall pass/fail status

**When to use:**
- Before creating a pull request
- To verify everything is working correctly
- As a final check before committing

### `type-check.sh` - Type Checking (Optional)
Runs mypy for static type analysis.

```bash
./scripts/type-check.sh
```

**What it does:**
- Runs mypy to check type hints and catch type-related errors
- Optional tool for projects with type annotations

**When to use:**
- When adding or updating type hints
- For stricter type safety verification
- Note: May report errors in code without full type annotations

## Individual Tool Usage

### Black (Code Formatter)
```bash
# Format specific files
uv run black backend/app.py

# Check without modifying
uv run black --check backend/

# Show what would change (diff mode)
uv run black --diff backend/
```

### isort (Import Sorter)
```bash
# Sort imports in specific files
uv run isort backend/app.py

# Check without modifying
uv run isort --check-only backend/

# Show what would change (diff mode)
uv run isort --diff backend/
```

### flake8 (Linter)
```bash
# Lint specific files
uv run flake8 backend/app.py

# Get detailed output
uv run flake8 --show-source backend/

# Count errors by type
uv run flake8 --statistics backend/
```

### mypy (Type Checker)
```bash
# Check specific files
uv run mypy backend/app.py

# Verbose output
uv run mypy --verbose backend/

# Generate HTML report
uv run mypy --html-report ./mypy-report backend/
```

## Configuration Files

- **pyproject.toml** - Configuration for black, isort, mypy, and pytest
- **.flake8** - Configuration for flake8 (doesn't support pyproject.toml)

## Git Pre-commit Hook (Optional)

To automatically run formatting before each commit:

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/format.sh
git add -u
EOF

chmod +x .git/hooks/pre-commit
```

## CI/CD Integration

For continuous integration, add to your workflow:

```bash
# Install dependencies
uv sync --extra dev --extra test

# Run checks
./scripts/check.sh
```

## Troubleshooting

### Scripts won't execute
```bash
chmod +x scripts/*.sh
```

### Import errors with mypy
Add the module to `tool.mypy.overrides` in pyproject.toml

### Flake8 conflicts with black
Black is configured to use 88 character lines and ignores E203, E501, W503 to be compatible with flake8.

## Best Practices

1. **Format early, format often** - Run `format.sh` regularly while developing
2. **Check before committing** - Run `lint.sh` to catch issues before they hit CI
3. **Complete verification** - Run `check.sh` before creating pull requests
4. **Update configs** - Adjust tool configurations in pyproject.toml and .flake8 as needed
