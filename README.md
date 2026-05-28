# Django Backend README

## Revisión General 🔍
Backend Django que proporciona APIs REST para PetCare. Incluye autenticación, modelos de datos y endpoints de API para operaciones CRUD comunes.

## Características ✅
- Django + Django REST Framework
- Soporte de PostgreSQL
- Migraciones y scripts de datos de semilla

## Requisitos 📄
- Python 3.10+
- pip
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL 12+

## Inicio rápido (desarrollo) 🚀
1. Clona el repositorio
   ```
   git clone <repo-url>
   cd <repo-folder>
   ```
2. Crea y activa el entorno virtual (opcional, pero recomendado)
   ```
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   ```
3. Instala dependencias
   ```
   pip install -r requirements.txt
   ```
4. Aplica migraciones y crea usuario superusuario
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Carga datos de semilla (opcional, aún no funcional)
   ```
   python scripts/seed_db.py
   ```
6. Corre el servidor de desarrollo
   ```
   python manage.py runserver
   ```

## Base de datos y Migraciones 📦
- Utiliza migraciones de Django. Para crear una migración:
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```
- Para vaciar la base de datos local (desarrollo):
  ```
  python scripts/reset_db.py
  ```

## API 🔌
- Ruta base: /api/

## Pruebas 📝
- Ejecuta pruebas con:
  ```
  python manage.py test
  ```

## CI/CD ⚒
- Pasos recomendados del pipeline:
  1. Instala dependencias
  2. Ejecuta linters (ruff)
  3. Ejecuta pruebas

## Registro & Monitoreo 📊
- Configura LOG_LEVEL mediante variables de entorno.

## Comandos comunes 💻
- Ejecuta la shell de Django:
  ```
  python manage.py shell
  ```
- Crea una migración para una app:
  ```
  python manage.py makemigrations <app_name>
  ```

## Contribución 🪛
- Clona el repositorio y crea/trabaja en una rama de característica.
- Incluye `#op<numero>` en tus mensajes de commit, sustituyendo `<numero>` por el número de paquete de trabajo en OpenProject relacionado con tu característica.
- Abre una solicitud de fusión, referenciando la URL corta del paquete de trabajo relacionado
  (por ejemplo: https://proyecto.paezweb.dev/wp/1234).
- Sigue el estilo de código: PEP8.

## Contacto / Soporte 📞
Accede a la sección de paquetes de trabajo en OpenProject para errores o solicitudes de funcionalidades.
