from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.permissions import IsRecepcionista
from apps.users.views import RecepcionistaTestView

User = get_user_model()

class IsRecepcionistaTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        # Crear usuario con grupo recepcionista
        self.recep_user = User.objects.create_user(username='recep_test', password='test')
        group, _ = Group.objects.get_or_create(name='recepcionista')
        self.recep_user.groups.add(group)
        # Crear usuario sin grupo
        self.other_user = User.objects.create_user(username='other_test', password='test')

    def test_recepcionista_has_permission(self):
        request = self.factory.get('/api/test-recepcionista/')
        force_authenticate(request, user=self.recep_user)
        perm = IsRecepcionista()
        self.assertTrue(perm.has_permission(request, None))

    def test_other_user_no_permission(self):
        request = self.factory.get('/api/test-recepcionista/')
        force_authenticate(request, user=self.other_user)
        perm = IsRecepcionista()
        self.assertFalse(perm.has_permission(request, None))

    def test_unauthenticated_no_permission(self):
        request = self.factory.get('/api/test-recepcionista/')
        perm = IsRecepcionista()
        self.assertFalse(perm.has_permission(request, None))