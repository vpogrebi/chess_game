#!/bin/bash

# Run tests with coverage and generate reports
echo "Running tests with coverage..."
python3.12 -m coverage run --source='.' manage.py test

echo "Generating coverage report..."
python3.12 -m coverage report

echo "Generating HTML coverage report..."
python3.12 -m coverage html

echo "Coverage report generated!"
echo "Terminal report: See above"
echo "HTML report: Open htmlcov/index.html in your browser"

# Optional: Open HTML report in browser
# open htmlcov/index.html
