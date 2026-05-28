# Revisión de contradicciones corregidas

## M2.1.1 Registro/autenticación
- Agregados endpoints `/auth/register/`, `/auth/login/`, `/auth/logout/`, `/auth/refresh/`, `/auth/me/`, `/auth/password/`.
- JWT con `user_id`, `email`, `role` y `JWT_SECRET_KEY` confirmado.
- `PetCareJWTAuthentication` sincroniza usuarios locales desde JWT de Módulo 5 para mantener FK estrictas del ERD.

## M2.1.2 CRUD propietarios
- `Owner.user_id` es PK, sin `Owner.id` artificial.
- `/owners/me/`, `/owners/me/pets/`, `/owners/me/appointments/`, `/owners/`, `/owners/{user_id}/`.
- Propietario ajeno recibe 403.

## M2.1.3 CRUD mascotas
- `Pet` usa tabla `patients` y `owner_id -> owners.user_id`.
- `DELETE` es soft delete.
- `MedicalRecord` se crea en la misma transacción al registrar mascota.
- No se usa `all_objects` para permitir operaciones normales sobre mascotas eliminadas.

## M2.2.1 Disponibilidad
- Slots pasados no se devuelven.
- Rango máximo de 30 días.
- Calendario default corregido al día actual.
- Recepción no puede modificar horarios.
- Generación de slots no bloquea GET `/slots/`; se encola con Celery.

## M2.2.2 Agendamiento
- `select_for_update()` sobre `TimeSlot`.
- Valida slot FREE, mascota activa, pertenencia, veterinario activo con rol VET.
- `Appointment.slot` ahora es FK y las restricciones activas son condicionales.

## M2.2.3 Cancelación
- Cancelación y liberación de slot en transacción.
- Slot cancelado puede reutilizarse por nueva cita.

## M2.2.4 Check-in/lista
- Recepción solamente.
- Evita doble check-in.
- Posición con bloqueo transaccional.
- `call-next` solo acepta el siguiente paciente real.

## M2.2.5 Confirmación/recordatorios
- Confirmación implementada.
- Señales usan `transaction.on_commit()`.
- Error de broker Celery no rompe la transacción HTTP.
- Notificación ajena devuelve 403.

## Validación realizada
- `python -m compileall` ejecutado correctamente sobre todo el proyecto.
- No se ejecutó `manage.py test` porque este entorno no tiene Django instalado; el ZIP incluye `requirements.txt` y tests para ejecutarlos localmente.
