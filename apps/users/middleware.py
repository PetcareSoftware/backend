import json
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import AuditLog
class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_body = ""
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not request.path.startswith('/admin/'):
            try:
                if request.body:
                    body_unicode = request.body.decode('utf-8')
                    try:
                        body_data = json.loads(body_unicode)
                        if 'password' in body_data:
                            body_data['password'] = '********'
                        request_body = json.dumps(body_data)
                    except json.JSONDecodeError:
                        request_body = body_unicode
            except Exception:
                request_body = "No se pudo capturar el cuerpo"

        response = self.get_response(request)

        # Registrar en la base de datos
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and not request.path.startswith('/admin/'):
            user = None
            try:
                auth = JWTAuthentication()
                auth_result = auth.authenticate(request)
                if auth_result:
                    user, token = auth_result
            except Exception:
                pass 

            AuditLog.objects.create(
                user=user,
                action=request.method,
                path=request.path,
                details=request_body
            )

        return response