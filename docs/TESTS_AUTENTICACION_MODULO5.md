# Pruebas de autenticación — responsabilidad Módulo 5 / Seguridad

Backend 1 no debe certificar la implementación interna de registro, login,
logout, refresh ni cambio de contraseña. Esos casos pertenecen al Módulo 5
(Seguridad).

Para Backend 1, la cobertura de autenticación queda limitada al contrato de
integración JWT:

```json
{
  "user_id": "uuid",
  "email": "usuario@ejemplo.com",
  "role": "OWNER | RECEPTIONIST | VET | TECH_VET | MANAGER"
}
```

Los tests de `tests/test_auth.py` validan que Backend 1:

1. acepta tokens firmados con `JWT_SECRET_KEY`;
2. rechaza tokens inválidos;
3. sincroniza una fila mínima local cuando el usuario del token aún no existe,
   para conservar integridad referencial con el ERD;
4. aplica permisos usando el claim `role`;
5. rechaza tokens sin datos suficientes para sincronizar usuarios;
6. rechaza usuarios locales inactivos.

Los casos de aceptación de `/auth/register/`, `/auth/login/`, `/auth/logout/`,
`/auth/refresh/` y `/auth/password/` deben quedar en la suite del Módulo 5 o en
pruebas end-to-end de integración entre módulos, no como pruebas unitarias de
Backend 1.
