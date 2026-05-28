from urllib.parse import urljoin

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AuthenticatedUserSerializer,
    AuthLoginProxySerializer,
    AuthLogoutProxySerializer,
    AuthRefreshProxySerializer,
    AuthRegisterProxySerializer,
    ChangePasswordSerializer,
)


def forward_to_security(request, *, path, serializer, method='post'):
    serializer.is_valid(raise_exception=True)

    base_url = getattr(settings, 'SECURITY_MODULE_BASE_URL', '').rstrip('/')
    if not base_url:
        return Response(
            {'detail': 'SECURITY_MODULE_BASE_URL no esta configurado para contactar el Modulo 5 de Seguridad.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    headers = {'Content-Type': 'application/json'}
    authorization = request.headers.get('Authorization')
    if authorization:
        headers['Authorization'] = authorization

    try:
        response = getattr(requests, method)(
            urljoin(f'{base_url}/', path),
            json=serializer.validated_data,
            headers=headers,
            timeout=getattr(settings, 'SECURITY_MODULE_TIMEOUT', 3),
        )
    except requests.Timeout:
        return Response(
            {'detail': 'Timeout al contactar el Modulo 5 de Seguridad.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except requests.RequestException:
        return Response(
            {'detail': 'Modulo 5 de Seguridad no disponible.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        payload = response.json() if response.content else {}
    except ValueError:
        payload = {'detail': response.text or 'Respuesta no JSON del Modulo 5.'}

    return Response(payload, status=response.status_code)


class AuthProxyView(APIView):
    action = None
    permission_classes = [AllowAny]
    serializer_classes = {
        'register': AuthRegisterProxySerializer,
        'login': AuthLoginProxySerializer,
        'refresh': AuthRefreshProxySerializer,
        'logout': AuthLogoutProxySerializer,
    }

    def post(self, request):
        serializer_class = self.serializer_classes[self.action]
        return forward_to_security(
            request,
            path=f'api/v1/auth/{self.action}/',
            serializer=serializer_class(data=request.data),
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(AuthenticatedUserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        return self._forward_to_security(request)

    def post(self, request):
        return self._forward_to_security(request)

    def _forward_to_security(self, request):
        return forward_to_security(
            request,
            path='api/v1/auth/password/',
            serializer=ChangePasswordSerializer(data=request.data),
            method='patch',
        )
