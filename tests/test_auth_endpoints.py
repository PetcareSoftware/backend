from unittest.mock import Mock, patch
from uuid import uuid4

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


def access_token(role='OWNER', email='usuario@test.com'):
    token = AccessToken()
    token['user_id'] = str(uuid4())
    token['email'] = email
    token['role'] = role
    return str(token)


def security_response(status_code=status.HTTP_200_OK, payload=None):
    response = Mock()
    response.status_code = status_code
    response.content = b'{}' if payload is not None else b''
    response.json.return_value = payload or {}
    response.text = ''
    return response


class AuthEndpointIntegrationTests(APITestCase):
    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token()}')

    def test_auth_me_rejects_request_without_token(self):
        res = self.client.get('/api/v1/auth/me/')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_me_returns_claims_from_module5_token(self):
        token = AccessToken()
        token['user_id'] = str(uuid4())
        token['email'] = 'owner@test.com'
        token['role'] = 'OWNER'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')

        res = self.client.get('/api/v1/auth/me/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], 'owner@test.com')
        self.assertEqual(res.data['role'], 'OWNER')

    @override_settings(SECURITY_MODULE_BASE_URL='http://security.test')
    @patch('apps.users.views.requests.post')
    def test_register_proxy_preserves_security_response(self, post_mock):
        payload = {
            'user': {'id': str(uuid4()), 'email': 'new@test.com', 'role': 'OWNER'},
            'tokens': {'access': 'access-token', 'refresh': 'refresh-token'},
        }
        post_mock.return_value = security_response(status.HTTP_201_CREATED, payload)

        res = self.client.post(
            '/api/v1/auth/register/',
            {
                'first_name': 'New',
                'last_name': 'Owner',
                'email': 'new@test.com',
                'password': 'Password123!',
                'password_confirm': 'Password123!',
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, payload)
        self.assertEqual(post_mock.call_args.args[0], 'http://security.test/api/v1/auth/register/')

    @override_settings(SECURITY_MODULE_BASE_URL='http://security.test')
    @patch('apps.users.views.requests.post')
    def test_login_refresh_and_logout_proxy_to_security(self, post_mock):
        post_mock.side_effect = [
            security_response(status.HTTP_200_OK, {'tokens': {'access': 'a', 'refresh': 'r'}}),
            security_response(status.HTTP_200_OK, {'access': 'new-access'}),
            security_response(status.HTTP_204_NO_CONTENT),
        ]

        login = self.client.post(
            '/api/v1/auth/login/',
            {'email': 'owner@test.com', 'password': 'Password123!'},
            format='json',
        )
        refresh = self.client.post('/api/v1/auth/refresh/', {'refresh': 'r'}, format='json')
        logout = self.client.post('/api/v1/auth/logout/', {'refresh': 'r'}, format='json')

        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertEqual(logout.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(post_mock.call_count, 3)
        self.assertEqual(post_mock.call_args_list[0].args[0], 'http://security.test/api/v1/auth/login/')
        self.assertEqual(post_mock.call_args_list[1].args[0], 'http://security.test/api/v1/auth/refresh/')
        self.assertEqual(post_mock.call_args_list[2].args[0], 'http://security.test/api/v1/auth/logout/')

    @override_settings(SECURITY_MODULE_BASE_URL='')
    def test_auth_proxy_requires_security_module_url(self):
        res = self.client.post(
            '/api/v1/auth/login/',
            {'email': 'owner@test.com', 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_register_validates_password_confirmation_before_proxy(self):
        res = self.client.post(
            '/api/v1/auth/register/',
            {
                'first_name': 'New',
                'last_name': 'Owner',
                'email': 'new@test.com',
                'password': 'Password123!',
                'password_confirm': 'Different123!',
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(SECURITY_MODULE_BASE_URL='')
    def test_change_password_requires_security_module_url(self):
        self.auth()

        res = self.client.patch(
            '/api/v1/auth/password/',
            {
                'old_password': 'Password123!',
                'new_password': 'NewPassword123!',
                'new_password_confirm': 'NewPassword123!',
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_change_password_validates_payload_before_proxy(self):
        self.auth()

        res = self.client.patch(
            '/api/v1/auth/password/',
            {
                'old_password': 'Password123!',
                'new_password': 'NewPassword123!',
                'new_password_confirm': 'Different123!',
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
