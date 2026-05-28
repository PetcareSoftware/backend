from rest_framework import status
from rest_framework.test import APITestCase


class OpenAPIContractTests(APITestCase):
    def test_schema_endpoint_is_public(self):
        res = self.client.get('/api/schema/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_swagger_docs_endpoint_is_public(self):
        res = self.client.get('/api/docs/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
