from mongoengine.connection import get_db
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Product
from .product_migration import migrate_legacy_product_categories
from .repository import clear_store


class ProductAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.base_url = "/products/"
        self.categories_url = "/products/categories/"
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

    def _create_product(self, **overrides):
        return self.client.post(self.base_url, self._payload(**overrides), format="json")

    def test_create_product_success(self):
        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["category"], "Electronics")
        self.assertEqual(response.data["data"]["brand"], "Acme")

    def test_brand_required_for_create(self):
        response = self._create_product(brand="")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("brand", response.data["errors"])

    def test_category_crud(self):
        created = self.client.post(
            self.categories_url,
            {"title": "Kitchen Essentials", "description": "Home and utility"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        category_id = created.data["data"]["id"]

        listed = self.client.get(self.categories_url)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data["data"]["count"], 1)

        detail = self.client.get(f"{self.categories_url}{category_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["data"]["title"], "Kitchen Essentials")

        patched = self.client.patch(
            f"{self.categories_url}{category_id}/",
            {"description": "Updated"},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["data"]["description"], "Updated")

        deleted = self.client.delete(f"{self.categories_url}{category_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_200_OK)

    def test_list_products_by_category(self):
        self._create_product(name="One", category="Food", price="10.00")
        self._create_product(name="Two", category="Food", price="20.00")
        self._create_product(name="Other", category="Electronics", price="30.00")

        categories = self.client.get(self.categories_url)
        food = [row for row in categories.data["data"]["results"] if row["title"] == "Food"][0]
        response = self.client.get(f"/products/categories/{food['id']}/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 2)

    def test_add_remove_products_from_category(self):
        p1 = self._create_product(name="P1", category="Food", price="1.00")
        p2 = self._create_product(name="P2", category="Kitchen", price="2.00")
        category = self.client.post(
            self.categories_url,
            {"title": "Kitchen Essentials", "description": ""},
            format="json",
        )
        category_id = category.data["data"]["id"]

        add = self.client.post(
            f"/products/categories/{category_id}/products/",
            {"product_ids": [p1.data["data"]["id"], p2.data["data"]["id"]]},
            format="json",
        )
        self.assertEqual(add.status_code, status.HTTP_200_OK)

        in_category = self.client.get(f"/products/categories/{category_id}/products/")
        self.assertEqual(in_category.data["data"]["count"], 2)

        remove = self.client.delete(
            f"/products/categories/{category_id}/products/",
            {"product_ids": [p1.data["data"]["id"]]},
            format="json",
        )
        self.assertEqual(remove.status_code, status.HTTP_200_OK)

    def test_bulk_csv_create(self):
        csv_payload = "\n".join(
            [
                "name,description,category_title,price,brand,warehouse_quantity",
                "Rice,Good grain,Food,100.00,Acme,4",
                "Pan,Steel pan,Kitchen Essentials,40.00,BrandX,5",
            ]
        )
        response = self.client.post(
            "/products/bulk/",
            data=csv_payload,
            content_type="text/csv",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["data"]), 2)

    def test_bulk_csv_validation_error_brand(self):
        csv_payload = "\n".join(
            [
                "name,description,category_title,price,brand,warehouse_quantity",
                "Rice,Good grain,Food,100.00,,4",
            ]
        )
        response = self.client.post(
            "/products/bulk/",
            data=csv_payload,
            content_type="text/csv",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_list_products_filter_by_category_ids(self):
        self._create_product(name="Cheap", category="Food", price="5.00")
        self._create_product(name="Spendy", category="Electronics", price="500.00")
        listed = self.client.get(self.categories_url)
        food_id = next(
            row["id"] for row in listed.data["data"]["results"] if row["title"] == "Food"
        )
        response = self.client.get(f"{self.base_url}?category_ids={food_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)
        self.assertEqual(response.data["data"]["results"][0]["name"], "Cheap")

    def test_list_products_unknown_category_id_returns_400(self):
        response = self.client.get(f"{self.base_url}?category_ids=999999")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("categories", response.data["errors"])

    def test_list_products_price_and_search_filters(self):
        self._create_product(name="Alpha Rice", category="Food", price="12.00")
        self._create_product(name="Beta Phone", category="Electronics", price="200.00")
        r = self.client.get(f"{self.base_url}?min_price=10&max_price=50&search=rice")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["data"]["count"], 1)
        self.assertEqual(r.data["data"]["results"][0]["name"], "Alpha Rice")

    def test_migrate_legacy_uncategorized_product(self):
        clear_store()
        now = Product.now_utc()
        product = Product(
            name="Orphan",
            description="",
            category_ref=None,
            price=9.99,
            brand="X",
            warehouse_quantity=1,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        product.save()
        stats = migrate_legacy_product_categories(dry_run=False)
        self.assertGreaterEqual(stats["assigned_uncategorized"], 1)
        product.reload()
        self.assertIsNotNone(product.category_ref)
        self.assertEqual(product.category_ref.title, "Uncategorized")

    def test_migrate_legacy_string_category_field(self):
        clear_store()
        now = Product.now_utc()
        product = Product(
            name="LegacyRow",
            description="",
            category_ref=None,
            price=1.0,
            brand="B",
            warehouse_quantity=0,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
        )
        product.save()
        get_db()["products"].update_one(
            {"id": product.id},
            {"$set": {"category": "VintageDept"}, "$unset": {"category_ref": ""}},
        )
        migrate_legacy_product_categories(dry_run=False)
        product.reload()
        self.assertIsNotNone(product.category_ref)
        self.assertEqual(product.category_ref.title, "VintageDept")
