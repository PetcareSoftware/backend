from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sqlite = BASE_DIR / 'db.sqlite3'
if sqlite.exists():
    sqlite.unlink()
print('Base de datos SQLite local eliminada. Ejecuta python manage.py migrate para recrearla.')
