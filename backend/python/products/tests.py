from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .repository import clear_store


class ProductAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = "/products/"
        clear_store()

    def _payload(self, **overrides):
        data = {
            "name": "Laptop Pro",
            "description": "A high performance laptop",
            "category": "Electronics",
            "price": "1200.00",
            "brand": "Acme",
            "warehouse_quantity": 25,
        }
        data.update(overrides)
        return data

    def test_create_product_success(self):
        response = self.client.post(self.base_url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Laptop Pro")
        self.assertIn("created_at", response.data["data"])
        self.assertIn("updated_at", response.data["data"])
        self.assertIsNotNone(response.data["data"]["created_at"])
        self.assertIsNotNone(response.data["data"]["updated_at"])

    def test_create_product_validation_error(self):
        response = self.client.post(
            self.base_url,
            self._payload(price="-10.00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("price", response.data["errors"])

    def test_get_product_and_get_missing_product(self):
        created = self.client.post(self.base_url, self._payload(), format="json")
        product_id = created.data["data"]["id"]

        response = self.client.get(f"{self.base_url}{product_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["id"], product_id)

        missing = self.client.get(f"{self.base_url}9999/")
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(missing.data["success"])

    def test_list_products_with_and_without_pagination(self):
        for index in range(3):
            self.client.post(
                self.base_url,
                self._payload(name=f"Product {index}", price=f"{index + 1}.00"),
                format="json",
            )

        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 3)
        self.assertEqual(len(response.data["data"]["results"]), 3)

        paged = self.client.get(f"{self.base_url}?page=1&page_size=2")
        self.assertEqual(paged.status_code, status.HTTP_200_OK)
        self.assertEqual(len(paged.data["data"]["results"]), 2)

    def test_update_invalid_field(self):
        created = self.client.post(self.base_url, self._payload(), format="json")
        product_id = created.data["data"]["id"]

        response = self.client.patch(
            f"{self.base_url}{product_id}/",
            {"warehouse_quantity": -1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("warehouse_quantity", response.data["errors"])

    def test_soft_delete_excludes_from_get_and_list(self):
        created = self.client.post(self.base_url, self._payload(), format="json")
        product_id = created.data["data"]["id"]

        deleted = self.client.delete(f"{self.base_url}{product_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)
        self.assertTrue(deleted.data["data"]["is_deleted"])

        get_response = self.client.get(f"{self.base_url}{product_id}/")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        list_response = self.client.get(self.base_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["data"]["count"], 0)

        include_deleted = self.client.get(f"{self.base_url}?include_deleted=true")
        self.assertEqual(include_deleted.status_code, status.HTTP_200_OK)
        self.assertEqual(include_deleted.data["data"]["count"], 1)

    def test_invalid_page_param_returns_400(self):
        response = self.client.get(f"{self.base_url}?page=0")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("page", response.data["errors"])

    def test_soft_delete_via_patch_deleted_field(self):
        created = self.client.post(self.base_url, self._payload(), format="json")
        product_id = created.data["data"]["id"]

        deleted = self.client.patch(
            f"{self.base_url}{product_id}/",
            {"deleted": True},
            format="json",
        )
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)
        self.assertTrue(deleted.data["data"]["is_deleted"])

        get_response = self.client.get(f"{self.base_url}{product_id}/")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        include_deleted = self.client.get(f"{self.base_url}?include_deleted=true")
        self.assertEqual(include_deleted.status_code, status.HTTP_200_OK)
        self.assertEqual(include_deleted.data["data"]["count"], 1)

    def test_patch_deleted_false_does_not_delete(self):
        created = self.client.post(self.base_url, self._payload(), format="json")
        product_id = created.data["data"]["id"]

        updated = self.client.patch(
            f"{self.base_url}{product_id}/",
            {"deleted": False},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)

        get_response = self.client.get(f"{self.base_url}{product_id}/")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertFalse(get_response.data["data"]["is_deleted"])

    def test_pagination_page_size_above_max_returns_400(self):
        for index in range(3):
            self.client.post(
                self.base_url,
                self._payload(name=f"Product {index}", price=f"{index + 1}.00"),
                format="json",
            )

        response = self.client.get(f"{self.base_url}?page_size=100")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("page_size", response.data["errors"])

    def test_invalid_created_after_returns_400(self):
        response = self.client.get(f"{self.base_url}?created_after=not-a-date")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("created_after", response.data["errors"])

