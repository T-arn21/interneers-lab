from mongoengine.connection import get_db
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from products.product_migration import migrate_legacy_product_categories
from products.test_utils import reset_products_test_data, seed_categories, seed_products


class ProductAPIE2EIntegrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = "/products/"
        self.categories_url = "/products/categories/"
        reset_products_test_data()
        self.categories = seed_categories()
        self.products = seed_products(self.categories)

    def tearDown(self):
        reset_products_test_data()

    def test_category_lifecycle_end_to_end(self):
        created = self.client.post(
            self.categories_url,
            {"title": "Fitness", "description": "Workout goods"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        category_id = created.data["data"]["id"]

        fetched = self.client.get(f"{self.categories_url}{category_id}/")
        self.assertEqual(fetched.status_code, status.HTTP_200_OK)
        self.assertEqual(fetched.data["data"]["title"], "Fitness")

        patched = self.client.patch(
            f"{self.categories_url}{category_id}/",
            {"description": "Updated"},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["data"]["description"], "Updated")

        deleted = self.client.delete(f"{self.categories_url}{category_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)

    def test_product_crud_and_soft_delete_end_to_end(self):
        created = self.client.post(
            self.base_url,
            {
                "name": "Desk Lamp",
                "description": "Bedside lamp",
                "category": "Electronics",
                "price": "42.50",
                "brand": "LightCo",
                "warehouse_quantity": 20,
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        pid = created.data["data"]["id"]

        fetched = self.client.get(f"{self.base_url}{pid}/")
        self.assertEqual(fetched.status_code, status.HTTP_200_OK)
        self.assertEqual(fetched.data["data"]["name"], "Desk Lamp")

        updated = self.client.patch(
            f"{self.base_url}{pid}/",
            {"warehouse_quantity": 15},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["data"]["warehouse_quantity"], 15)

        deleted = self.client.delete(f"{self.base_url}{pid}/")
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)
        self.assertTrue(deleted.data["data"]["is_deleted"])

        hidden = self.client.get(f"{self.base_url}{pid}/")
        self.assertEqual(hidden.status_code, status.HTTP_404_NOT_FOUND)
        included = self.client.get(f"{self.base_url}{pid}/?include_deleted=true")
        self.assertEqual(included.status_code, status.HTTP_200_OK)

    def test_rich_filters_end_to_end(self):
        categories = self.client.get(self.categories_url).data["data"]["results"]
        electronics_id = next(row["id"] for row in categories if row["title"] == "Electronics")

        by_category = self.client.get(f"{self.base_url}?category_ids={electronics_id}")
        self.assertEqual(by_category.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["category"] == "Electronics" for p in by_category.data["data"]["results"]))

        by_price = self.client.get(f"{self.base_url}?min_price=25&max_price=60")
        self.assertEqual(by_price.status_code, status.HTTP_200_OK)
        self.assertTrue(
            all(25 <= p["price"] <= 60 for p in by_price.data["data"]["results"])
        )

        by_brand_and_search = self.client.get(f"{self.base_url}?brand_contains=ac&search=pan")
        self.assertEqual(by_brand_and_search.status_code, status.HTTP_200_OK)
        self.assertEqual(by_brand_and_search.data["data"]["count"], 1)
        self.assertEqual(by_brand_and_search.data["data"]["results"][0]["name"], "Steel Pan")

        has_category = self.client.get(f"{self.base_url}?has_category=true")
        self.assertEqual(has_category.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(has_category.data["data"]["count"], 1)

    def test_migration_links_legacy_category_string(self):
        target = self.products[0]
        get_db()["products"].update_one(
            {"id": target.id},
            {"$set": {"category": "LegacyElectronics"}, "$unset": {"category_ref": ""}},
        )

        stats = migrate_legacy_product_categories(dry_run=False)
        self.assertGreaterEqual(stats["linked_from_legacy_category_string"], 1)

        out = self.client.get(f"{self.base_url}{target.id}/")
        self.assertEqual(out.status_code, status.HTTP_200_OK)
        self.assertEqual(out.data["data"]["category"], "LegacyElectronics")
