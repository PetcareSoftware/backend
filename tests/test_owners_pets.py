from rest_framework import status
from tests.base import PetCareAPITestCase
from apps.pets.models import Pet


class OwnersPetsTests(PetCareAPITestCase):
    def test_owner_me_and_patch(self):
        self.auth(self.owner_user)
        res = self.client.get('/api/v1/owners/me/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        patch = self.client.patch('/api/v1/owners/me/', {'first_name':'Nuevo','email':'hack@test.com'}, format='json')
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.owner_user.refresh_from_db()
        self.assertEqual(self.owner_user.email, 'owner@test.com')

    def test_owner_list_permissions_and_receptionist_list(self):
        self.auth(self.owner_user)
        self.assertEqual(self.client.get('/api/v1/owners/').status_code, status.HTTP_403_FORBIDDEN)
        self.auth(self.receptionist)
        res = self.client.get('/api/v1/owners/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)

    def test_owner_cannot_retrieve_other_owner(self):
        self.auth(self.owner_user)
        res = self.client.get(f'/api/v1/owners/{self.other_owner.user_id}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_pet_ignores_foreign_owner(self):
        self.auth(self.owner_user)
        res = self.client.post('/api/v1/owners/me/pets/', {'name':'Rocky','breed_id':str(self.breed.id),'owner_id':str(self.other_owner.user_id)}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        pet = Pet.objects.get(id=res.data['id'])
        self.assertEqual(pet.owner_id, self.owner_user.id)
        self.assertTrue(hasattr(pet, 'medical_record'))

    def test_soft_delete_and_not_returned_in_owner_pets(self):
        self.auth(self.owner_user)
        deleted = self.client.delete(f'/api/v1/pets/{self.pet.id}/')
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Pet.all_objects.get(id=self.pet.id).is_deleted)
        pets = self.client.get('/api/v1/owners/me/pets/')
        self.assertFalse(any(str(p['id']) == str(self.pet.id) for p in pets.data))

    def test_delete_with_active_appointment_409(self):
        self.create_appointment()
        self.auth(self.owner_user)
        res = self.client.delete(f'/api/v1/pets/{self.pet.id}/')
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)

    def test_owner_cannot_update_other_pet(self):
        self.auth(self.owner_user)
        res = self.client.patch(f'/api/v1/pets/{self.other_pet.id}/', {'name':'Hack'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
