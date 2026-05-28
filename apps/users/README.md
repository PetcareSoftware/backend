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

# Panel de Logs de Auditoría (M5.2.4)

## Descripción
Interfaz web protegida que permite al **Gerente** visualizar, filtrar y paginar los registros históricos de eventos del sistema, capturados automáticamente por el middleware de auditoría.

## Requisitos previos
- El modelo `RegistroAuditoria` y el middleware `AuditoriaMiddleware` deben estar migrados y activos.
- El grupo **Gerente** debe existir y contener al menos un usuario.
- La autenticación por sesión y JWT están habilitadas.

## Cómo acceder
1. Navegue a `/panel-logs/`.
2. Si no ha iniciado sesión, será redirigido al formulario de login.
3. Ingrese las credenciales de un usuario que pertenezca al grupo `Gerente`.
4. Tras el login, verá el panel con la tabla de eventos.

## Estructura del modelo `RegistroAuditoria`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | BigAutoField | Identificador único del registro |
| `usuario` | FK a User | Usuario que realizó la acción (puede ser nulo) |
| `accion` | CharField | Método HTTP o acción semántica (login, access_granted, etc.) |
| `ruta` | CharField | Ruta solicitada |
| `fecha` | DateTime | Momento del evento |
| `detalles` | TextField | Cuerpo de la petición (con contraseñas ofuscadas) |

## Endpoint REST
- **URL:** `/api/logs/`
- **Método:** GET
- **Autenticación:** JWT o sesión
- **Permiso requerido:** Pertencer al grupo `Gerente`
- **Parámetros opcionales:**
  - `user_id` – ID del usuario
  - `desde` – Fecha/hora de inicio (ISO 8601)
  - `hasta` – Fecha/hora de fin (ISO 8601)
  - `action` – Tipo de acción (ej. `login`, `POST`)
- **Paginación:** 20 resultados por página

## Vistas y archivos relevantes
- Modelo: `apps/users/models.py` (`RegistroAuditoria`)
- Serializador: `apps/users/serializers.py` (`RegistroAuditoriaSerializer`)
- Vistas: `apps/users/views.py` (`LogEntryListView`, `PanelLogsView`)
- Permisos: `apps/users/permissions.py` (`esGerente`)
- Middleware: `apps/users/middleware.py` (`AuditoriaMiddleware`)
- Plantilla: `templates/panel_logs.html`
- Login: `templates/registration/login.html`
- Rutas: `apps/users/urls.py` y `config/urls.py`