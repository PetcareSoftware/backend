#!/usr/bin/env bash
set -euo pipefail
rm -f db.sqlite3
python manage.py migrate
python scripts/seed_db.py
