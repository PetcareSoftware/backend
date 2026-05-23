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


---

# Módulo de Seguridad – Panel de Logs de Auditoría (M5.2.4)

## Descripción
Interfaz web protegida que permite al **Gerente** visualizar, filtrar y paginar los registros históricos de eventos del sistema (auditoría).

## Requisitos previos
- El modelo `LogEntry` debe estar migrado (`apps/users/models.py`).
- El grupo **Gerente** debe existir y contener al menos un usuario.
- La autenticación por sesión (`django.contrib.auth`) y JWT están activas.

## Cómo acceder
1. Navegue a `/panel-logs/`.
2. Si no está autenticado, será redirigido al formulario de inicio de sesión.
3. Ingrese las credenciales de un usuario que pertenezca al grupo `Gerente`.
4. Tras el login, verá el panel con la tabla de eventos.

## Estructura del modelo `LogEntry`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `timestamp` | DateTime | Fecha y hora del evento |
| `user` | FK a User | Usuario que generó el evento (puede ser nulo) |
| `action` | CharField | Tipo de evento (login, access_granted, etc.) |
| `details` | TextField | Información adicional |
| `ip_address` | IPAddressField | Dirección IP de origen |

## Endpoint REST
- **URL:** `/api/logs/`
- **Método:** GET
- **Autenticación:** JWT o sesión
- **Permiso requerido:** Pertencer al grupo `Gerente`
- **Parámetros opcionales:**
  - `user_id` – ID del usuario
  - `desde` – Fecha/hora de inicio (ISO 8601)
  - `hasta` – Fecha/hora de fin (ISO 8601)
  - `action` – Tipo de acción (ej. `login`)
- **Paginación:** 20 resultados por página

## Vistas y archivos relevantes
- Modelo: `apps/users/models.py` (clase `LogEntry`)
- Serializador: `apps/users/serializers.py` (`LogEntrySerializer`)
- Vistas: `apps/users/views.py` (`LogEntryListView`, `PanelLogsView`)
- Permisos: `apps/users/permissions.py` (`esGerente`)
- Plantilla: `templates/panel_logs.html`
- Login: `templates/registration/login.html`
- Rutas: `apps/users/urls.py` y `config/urls.py`