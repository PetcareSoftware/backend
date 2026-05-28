
# Django Backend README

## Project Overview 🔍
A Django backend providing REST APIs for PetCare. Includes authentication, data models, and API endpoints for common CRUD operations.

## Features ✅
- Django + Django REST Framework
- PostgreSQL support
- Migrations and seed data scripts

## Requirements 📄
- Python 3.10+
- pip
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL 12+

## Quick start (development) 🚀
1. Clone repository
   ```
   git clone <repo-url>
   cd <repo-folder>
   ```
2. Create and activate virtual environment (optional, but recommended)
   ```
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Apply migrations and create superuser
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Load seed data (optional, no yet functional)
   ```
   python scripts/seed_db.py
   ```
6. Run development server
   ```
   python manage.py runserver
   ```

## Database & Migrations 📦
- Uses Django migrations. To create a migration:
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```
- To reset local DB (development):
  ```
  python scripts/reset_db.py
  ```

## API 🔌
- Base path: /api/

## Testing 📝
- Run tests with:
  ```
  python manage.py test
  ```

## CI/CD ⚒️
- Recommended pipeline steps:
  1. Install dependencies
  2. Run linters (ruff)
  3. Run tests

## Logging & Monitoring 📊
- Configure LOG_LEVEL via environment variables.

## Common Commands 💻
- Run shell:
  ```
  python manage.py shell
  ```
- Create migration for app:
  ```
  python manage.py makemigrations <app_name>
  ```

## Contributing 🪛
- Clone the repo and create/work in a feature branch.
- Include `#op<number>` in your commit messages, substituting `<number>`
  for the work package number in OpenProject related to your feature.
- Open a pull request, referencing the short URL of the related
  work package (eg. https://proyecto.paezweb.dev/wp/1234).
- Follow code style: PEP8.

## Contact / Support 📞
Open issues in OpenProject for bugs or feature requests.
