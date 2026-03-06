# Code Coverage

This project uses Python's `coverage` module to measure test coverage.

## Running Coverage

### Quick Run
```bash
./run_coverage.sh
```

### Manual Run
```bash
# Run tests with coverage
python3.12 -m coverage run --source='.' manage.py test

# Generate terminal report
python3.12 -m coverage report

# Generate HTML report
python3.12 -m coverage html
```

## Coverage Report

Current coverage: **70%** overall

### File-by-file coverage:
- `chess/models.py`: 98% (95/95 statements)
- `chess/game_logic.py`: 69% (269/389 statements)
- `chess/views.py`: 64% (127/198 statements)
- `chess/middleware.py`: 100% (8/8 statements)
- `chess/admin.py`: 100% (8/8 statements)
- `chess/urls.py`: 100% (4/4 statements)

### Files needing more coverage:
1. **chess/game_logic.py** (69%) - Core chess logic implementation
2. **chess/views.py** (64%) - Django views for web interface

## HTML Report

Open `htmlcov/index.html` in your browser to view detailed coverage visualization.

## Configuration

Coverage is configured via `.coveragerc`:
- Excludes: migrations, venv, cache files, tests
- Reports: Terminal and HTML output
- HTML directory: `htmlcov/`
