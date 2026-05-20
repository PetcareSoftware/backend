# Módulo de Seguridad – Autorización del Recepcionista

Este documento explica cómo usar la autorización del rol **Recepcionista** en las vistas del backend.

## Requisitos previos
- La autenticación debe estar funcionando (ver `sec/feature/autenticacion-usuarios`).
- Las migraciones de `users` deben estar aplicadas (se crean automáticamente los permisos y el grupo `recepcionista`).

## Permisos creados
La migración `0001_create_recepcionista_permissions` (o similar) crea los siguientes permisos:
- `auth.add_manual_appointment`
- `auth.view_calendar_availability`
- `auth.register_attendance`
- `auth.manage_waitlist`
- `auth.view_appointment_history`

Estos permisos se asignan automáticamente al grupo **`recepcionista`**.

## Cómo proteger una vista

1. Importa la clase de permiso:
```python
from apps.users.permissions import IsRecepcionista
from rest_framework.permissions import IsAuthenticated
