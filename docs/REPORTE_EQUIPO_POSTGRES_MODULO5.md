# Reporte para el equipo — pruebas PostgreSQL y coordinación con Módulo 5

## 1. Prueba de concurrencia de citas

La prueba `tests/test_concurrency.py::AppointmentConcurrencyTests` está marcada con `skipIf(connection.vendor == 'sqlite', ...)` porque `select_for_update()` no tiene semántica transaccional real en SQLite. Esto es correcto técnicamente, pero implica que un entorno local SQLite **no ejecuta** el caso crítico de dos reservas simultáneas del mismo slot.

Acción requerida antes de merge:

- Ejecutar la suite en PostgreSQL en CI.
- Usar el workflow `.github/workflows/django-postgres-tests.yml` incluido en este patch.
- Bloquear merge si falla `python manage.py test` contra PostgreSQL.

## 2. Riesgo de doble modelo User con Módulo 5 Seguridad

El proyecto mantiene `apps/users/models.py` con las tablas `users`, `roles`, `clinical_staff` y `veterinarians` porque Backend 1 necesita llaves foráneas locales según el ERD y Django necesita `AUTH_USER_MODEL` para autenticación/permisos.

Esto debe confirmarse con Mario / Módulo 5 antes de integrar bases de datos. Riesgo principal:

- Si Seguridad también crea y migra su propia tabla `users` incompatible, puede haber choque de ownership de tabla, migraciones o datos.

Decisión requerida:

1. **Mirror local coordinado:** Backend 1 mantiene una copia local sincronizada de `users`/`roles`, con UUID proveniente del JWT de Seguridad.
2. **BD compartida:** Módulo 5 es dueño de las tablas `users`/`roles` y Backend 1 solo referencia esas tablas con migraciones coordinadas.
3. **Sin tabla local de usuarios:** Backend 1 reemplaza FKs a `User` por UUID planos y adapta autenticación/permisos. Esta opción requiere refactor mayor porque afecta Owners, Staff, Vets, Citas, Consultas y Vacunación.

Hasta que se tome una decisión, este repositorio debe tratar `apps/users` como implementación local de compatibilidad, no como contrato definitivo de Seguridad.
