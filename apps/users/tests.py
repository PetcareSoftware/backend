from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.users.permissions import IsReceptionist
from apps.users.views import ReceptionistTestView

User = get_user_model()

class IsReceptionistTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Crear usuario con grupo recepcionista
        self.receptionist_user = User.objects.create_user(username='receptionist_test', password='test')
        group, _ = Group.objects.get_or_create(name='receptionist')
        self.receptionist_user.groups.add(group)
        
        # Crear usuario sin grupo
        self.other_user = User.objects.create_user(username='other_test', password='test')

    def test_receptionist_has_permission(self):
        request = self.factory.get('/api/test-receptionist/')
        force_authenticate(request, user=self.receptionist_user)
        perm = IsReceptionist()
        self.assertTrue(perm.has_permission(request, None))

    def test_other_user_no_permission(self):
        request = self.factory.get('/api/test-receptionist/')
        force_authenticate(request, user=self.other_user)
        perm = IsReceptionist()
        self.assertFalse(perm.has_permission(request, None))

    def test_unauthenticated_no_permission(self):
        request = self.factory.get('/api/test-receptionist/')
        perm = IsReceptionist()
        self.assertFalse(perm.has_permission(request, None))