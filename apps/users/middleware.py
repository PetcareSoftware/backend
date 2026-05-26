import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RegistroAuditoria

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #Leer los datos que se van a alterar antes de que la vista lo procese
        cuerpo_peticion = ""
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not request.path.startswith('/admin/'):
            try:
                if request.body:
                    body_unicode = request.body.decode('utf-8')
                    try:
                        # Si es formato JSON, ocultamos contraseñas por seguridad
                        body_data = json.loads(body_unicode)
                        if 'password' in body_data:
                            body_data['password'] = '********'
                        cuerpo_peticion = json.dumps(body_data)
                    except json.JSONDecodeError:
                        cuerpo_peticion = body_unicode
            except Exception:
                cuerpo_peticion = "No se pudo capturar el cuerpo"

        response = self.get_response(request)

        #Registrar en la base de datos
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not request.path.startswith('/admin/'):
            user = None
            try:
                auth = JWTAuthentication()
                auth_result = auth.authenticate(request)
                if auth_result:
                    user, token = auth_result
            except Exception:
                pass 

            # Guardamos toda la evidencia en la libreta
            RegistroAuditoria.objects.create(
                usuario=user,
                accion=request.method,
                ruta=request.path,
                detalles=cuerpo_peticion  
            )

        return response