# PetCare Backend 1

Backend Django/DRF para el módulo Backend 1 de PetCare: citas, agenda, historial clínico, notificaciones, consumo de insumos y vacunación.

## Stack

- Python 3.10+
- Django 5.2
- Django REST Framework 3.16
- SimpleJWT
- PostgreSQL 12+ en producción; SQLite permitido en desarrollo local
- Celery para recordatorios/reintentos

## Base URL

La ruta base formal del contrato Backend 1 → Frontend 1 es:

```txt
/api/v1/
```

> Nota: si algún README previo indicaba `/api/`, esa línea queda corregida. El catálogo de rutas y el contrato JSON usan `/api/v1/`.

## Variables de entorno

Copia `.env.example` a `.env` y configura:

```env
JWT_SECRET_KEY=django-insecure-pv%6v^123!@#_petcare_security_key_2026_v1
DATABASE_URL=sqlite:///db.sqlite3
CELERY_BROKER_URL=redis://localhost:6379/0
BACKEND2_INVENTORY_URL=http://localhost:8002/api/v1
```

Payload JWT esperado desde Módulo 5:

```json
{
  "user_id": "uuid",
  "email": "usuario@ejemplo.com",
  "role": "OWNER",
  "is_active": true
}
```

Roles válidos: `OWNER`, `RECEPTIONIST`, `VET`, `TECH_VET`, `MANAGER`.

> Coordinación pendiente: este repo contiene `apps/users` como implementación local de compatibilidad con el ERD y las FK internas. Debe confirmarse con Módulo 5 si esas tablas serán espejo local, BD compartida o reemplazadas por referencias UUID. Ver `docs/REPORTE_EQUIPO_POSTGRES_MODULO5.md`.

## Inicio rápido

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

## Reset de base local

Se incluyen ambos formatos para eliminar la contradicción documental:

```bash
python scripts/reset_db.py
# o
bash scripts/reset_db.sh
```

Después ejecuta:

```bash
python manage.py migrate
```

## Semilla

```bash
python scripts/seed_db.py
```

## Pruebas

```bash
python manage.py test
```

Las pruebas incluidas cubren los mínimos principales de M2.1, M2.2 y M2.3: autenticación, owners/pets, disponibilidad, citas, cancelación, check-in/lista, notificaciones, historial clínico, consultas, prescripciones, adjuntos, insumos y vacunación.

### Prueba obligatoria en PostgreSQL

La prueba de concurrencia de reservas usa `select_for_update()`. SQLite no reproduce esa semántica transaccional, por lo que `tests/test_concurrency.py` se omite automáticamente en SQLite. Para que el criterio de concurrencia se valide antes de merge, la suite debe ejecutarse también en PostgreSQL. Se incluye el workflow:

```txt
.github/workflows/django-postgres-tests.yml
```

Ese workflow levanta PostgreSQL y ejecuta `python manage.py test`; debe ser requerido en PR antes de integrar cambios.

## Endpoints principales

- `/api/v1/auth/register/`
- `/api/v1/auth/login/`
- `/api/v1/auth/logout/`
- `/api/v1/auth/refresh/`
- `/api/v1/auth/me/`
- `/api/v1/auth/password/`
- `/api/v1/owners/me/`
- `/api/v1/owners/me/pets/`
- `/api/v1/pets/{id}/medical-record/`
- `/api/v1/pets/{id}/medical-record/summary/`
- `/api/v1/pets/{id}/vaccination-plan/`
- `/api/v1/pets/{id}/vaccination-plan/schedule/`
- `/api/v1/pets/{id}/vaccination-events/`
- `/api/v1/vets/{id}/slots/`
- `/api/v1/vets/{id}/availability/`
- `/api/v1/schedules/calendar/`
- `/api/v1/appointments/`
- `/api/v1/appointments/{id}/cancel/`
- `/api/v1/appointments/{id}/confirm/`
- `/api/v1/appointments/{id}/check-in/`
- `/api/v1/appointments/{id}/consultations/`
- `/api/v1/waiting-list/`
- `/api/v1/waiting-list/{id}/call-next/`
- `/api/v1/consultations/{id}/`
- `/api/v1/consultations/{id}/prescriptions/`
- `/api/v1/consultations/{id}/attachments/`
- `/api/v1/consultations/{id}/supplies-used/`
- `/api/v1/notifications/`
- `/api/v1/notifications/{id}/read/`


## Integración JWT con Módulo 5 sin tocar modelos

Backend 1 no implementa register/login/logout/refresh ni crea usuarios locales. La identidad pertenece al Módulo 5 de Seguridad. Backend 1 valida el JWT firmado con `JWT_SECRET_KEY`, construye un usuario en memoria para `request.user` y autoriza usando el claim `role`.

Claims mínimos aceptados:

```json
{
  "user_id": "uuid-v4",
  "email": "usuario@ejemplo.com",
  "role": "OWNER"
}
```

Roles válidos: `OWNER`, `RECEPTIONIST`, `VET`, `TECH_VET`, `MANAGER`.

El claim `is_active` es opcional por compatibilidad; si viene en `false`, el request se rechaza con 401. No se modifica ningún `models.py`, no se crean migraciones y no se usa `User.objects.get_or_create()` en autenticación.
