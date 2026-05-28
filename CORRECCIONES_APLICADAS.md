# Correcciones aplicadas

## Contradicciones externas

1. Base URL corregida a `/api/v1/` en README, alineada con catálogo y contrato formal.
2. Se agregaron ambos scripts de reset: `scripts/reset_db.py` y `scripts/reset_db.sh`.
3. Se mantiene autenticación local `/auth/*` para cumplir M2.1.1 y compatibilidad JWT con Módulo 5 mediante `JWT_SECRET_KEY`, `user_id`, `email`, `role`.
4. Se documenta la contradicción de “registro único público”; por contrato funcional, `register`, `login` y `refresh` son públicos.

## M2.1

- Tests ampliados para registro, login, logout, refresh y cambio de contraseña.
- `Owner.user_id` se mantiene como PK según ERD.
- `OwnerViewSet` usa clases de permiso para list/retrieve/me sin filtrar detalle a 404 cuando debe ser 403.
- `Pet` hereda de `BaseModel` y usa manager activo por defecto.
- Soft delete y validación de citas activas permanecen en `PetService`.

## M2.2

- `PATCH /appointments/{id}/` corrige `slot_id -> new_slot_id`.
- Reprogramación valida slots pasados.
- Cancelación ajena devuelve 403.
- Manager ya no cancela/confirma por defecto si el criterio solo menciona owner/recepción.
- Check-in exitoso devuelve 200; check-in doble devuelve 409.
- Waiting-list queda restringida a recepción/veterinarios.
- Confirmación solo permite `SCHEDULED -> CONFIRMED`.
- Celery se encola desde signal con `eta` 24h/48h antes, usando `transaction.on_commit()`.
- Las tareas verifican estado actual y no notifican citas canceladas/completadas.
- Errores de tarea se registran en `NotificationLog` como `FAILED`.

## M2.3

- Se implementan endpoints de expediente completo y summary.
- `clinical_notes` se oculta para owners.
- Registro de consulta se hace por `/appointments/{id}/consultations/`, solo vet asignado y solo en `CHECKED_IN`.
- La cita pasa a `COMPLETED` mediante signal `on_consultation_created`.
- Edición de consulta tiene ventana de 24 horas en serializer.
- Prescripciones y adjuntos funcionan con validación de PDF/JPG/PNG y 10 MB.
- Adjuntos se almacenan en `MEDIA_ROOT/attachments/{consultation_id}/`.
- `InventoryClient` encapsula Backend 2 con timeout de 3 segundos.
- `supplies-used` maneja stock insuficiente 409, supply inexistente 404 y Backend 2 caído como `PENDING_SYNC`.
- Vacunación usa rutas nested por mascota, cronograma PENDING/APPLIED/OVERDUE y eventos con `batch_number`/`applied_date`.
- `/appointments/today/by-vet/{vet_id}/` restringe al veterinario propio.
- `/pets/{id}/appointments/` queda paginado.
