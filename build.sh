#!/usr/bin/env bash
set -o errexit  # stop if any command fails

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Collect static files (CSS, JS) into a folder called 'staticfiles'
python manage.py collectstatic --no-input

# 3. Apply database migrations
python manage.py migrate --no-input
