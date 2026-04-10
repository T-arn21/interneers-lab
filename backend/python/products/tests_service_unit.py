from unittest.mock import patch

from django.test import SimpleTestCase

from products.product_category_service import ProductCategoryService
from products.service import ProductService


class ProductServiceUnitTests(SimpleTestCase):
    @patch("products.service.repo.create_product")
    def test_create_delegates_to_repository(self, create_product_mock):
        payload = {"name": "A"}
        create_product_mock.return_value = object()

        out = ProductService.create(payload)

        self.assertIs(out, create_product_mock.return_value)
        create_product_mock.assert_called_once_with(payload)

    @patch("products.service.repo.create_product")
    def test_create_bulk_creates_each_payload(self, create_product_mock):
        p1, p2 = object(), object()
        create_product_mock.side_effect = [p1, p2]

        out = ProductService.create_bulk([{"name": "A"}, {"name": "B"}])

        self.assertEqual(out, [p1, p2])
        self.assertEqual(create_product_mock.call_count, 2)

    @patch("products.service.repo.get_product")
    def test_get_product_delegates(self, get_product_mock):
        get_product_mock.return_value = object()
        out = ProductService.get_product(7, include_deleted=True)
        self.assertIs(out, get_product_mock.return_value)
        get_product_mock.assert_called_once_with(7, include_deleted=True)

    @patch("products.service.repo.get_product")
    @patch("products.service.repo.soft_delete_product")
    def test_soft_delete_when_found(self, soft_delete_mock, get_product_mock):
        product = object()
        get_product_mock.return_value = product
        soft_delete_mock.return_value = object()

        out = ProductService.soft_delete(3)

        self.assertIs(out, soft_delete_mock.return_value)
        get_product_mock.assert_called_once_with(3, include_deleted=False)
        soft_delete_mock.assert_called_once_with(product)

    @patch("products.service.repo.get_product")
    def test_soft_delete_when_missing(self, get_product_mock):
        for product_id in (1, 3, 99):
            with self.subTest(product_id=product_id):
                get_product_mock.reset_mock()
                get_product_mock.return_value = None
                out = ProductService.soft_delete(product_id)
                self.assertIsNone(out)
                get_product_mock.assert_called_once_with(product_id, include_deleted=False)

    @patch("products.service.repo.get_product")
    @patch("products.service.repo.soft_delete_product")
    @patch("products.service.repo.update_product")
    def test_update_parameterized_branches(self, update_product_mock, soft_delete_mock, get_product_mock):
        scenarios = [
            {
                "name": "missing_product",
                "product": None,
                "payload": {"name": "new"},
                "expect_none": True,
                "expect_soft_delete": False,
                "expect_update_payload": None,
            },
            {
                "name": "deleted_true",
                "product": object(),
                "payload": {"deleted": True},
                "expect_none": False,
                "expect_soft_delete": True,
                "expect_update_payload": None,
            },
            {
                "name": "deleted_false_only",
                "product": object(),
                "payload": {"deleted": False},
                "expect_none": False,
                "expect_soft_delete": False,
                "expect_update_payload": {},
            },
            {
                "name": "normal_payload",
                "product": object(),
                "payload": {"name": "N", "price": 3.2},
                "expect_none": False,
                "expect_soft_delete": False,
                "expect_update_payload": {"name": "N", "price": 3.2},
            },
        ]

        for scenario in scenarios:
            with self.subTest(case=scenario["name"]):
                product = scenario["product"]
                get_product_mock.reset_mock()
                update_product_mock.reset_mock()
                soft_delete_mock.reset_mock()
                get_product_mock.return_value = product
                update_product_mock.return_value = object()
                soft_delete_mock.return_value = object()

                out = ProductService.update(5, scenario["payload"])

                if scenario["expect_none"]:
                    self.assertIsNone(out)
                    update_product_mock.assert_not_called()
                    soft_delete_mock.assert_not_called()
                    continue

                if scenario["expect_soft_delete"]:
                    self.assertIs(out, soft_delete_mock.return_value)
                    soft_delete_mock.assert_called_once_with(product)
                    update_product_mock.assert_not_called()
                    continue

                self.assertIs(out, update_product_mock.return_value)
                update_product_mock.assert_called_once_with(product, scenario["expect_update_payload"])
                soft_delete_mock.assert_not_called()

    @patch("products.service.resolve_categories_for_filter")
    @patch("products.service.repo.list_products")
    def test_list_products_resolves_categories_and_forwards_filters(
        self, list_products_mock, resolve_categories_mock
    ):
        cats = [object()]
        resolve_categories_mock.return_value = cats
        list_products_mock.return_value = [object()]

        out = ProductService.list_products(
            include_deleted=True,
            category_ids=[1],
            category_titles=["Food"],
            min_price=1.0,
            max_price=10.0,
            has_category=True,
        )

        self.assertIs(out, list_products_mock.return_value)
        resolve_categories_mock.assert_called_once_with(category_ids=[1], category_titles=["Food"])
        self.assertEqual(list_products_mock.call_args.kwargs["filter_categories"], cats)
        self.assertEqual(list_products_mock.call_args.kwargs["min_price"], 1.0)
        self.assertEqual(list_products_mock.call_args.kwargs["max_price"], 10.0)
        self.assertEqual(list_products_mock.call_args.kwargs["has_category"], True)

    @patch("products.service.resolve_categories_for_filter")
    @patch("products.service.repo.list_products")
    def test_list_products_without_category_filters_does_not_resolve(
        self, list_products_mock, resolve_categories_mock
    ):
        list_products_mock.return_value = []
        ProductService.list_products()
        resolve_categories_mock.assert_not_called()
        self.assertIsNone(list_products_mock.call_args.kwargs["filter_categories"])


class ProductCategoryServiceUnitTests(SimpleTestCase):
    @patch("products.product_category_service.repo.create_category")
    def test_create_delegates(self, create_category_mock):
        payload = {"title": "Food"}
        create_category_mock.return_value = object()
        out = ProductCategoryService.create(payload)
        self.assertIs(out, create_category_mock.return_value)
        create_category_mock.assert_called_once_with(payload)

    @patch("products.product_category_service.repo.list_categories")
    def test_list_categories_delegates(self, list_categories_mock):
        list_categories_mock.return_value = [object()]
        out = ProductCategoryService.list_categories()
        self.assertEqual(out, list_categories_mock.return_value)

    @patch("products.product_category_service.repo.get_category")
    def test_get_delegates(self, get_category_mock):
        get_category_mock.return_value = object()
        out = ProductCategoryService.get(3)
        self.assertIs(out, get_category_mock.return_value)
        get_category_mock.assert_called_once_with(3)

    @patch("products.product_category_service.repo.get_category")
    @patch("products.product_category_service.repo.update_category")
    @patch("products.product_category_service.repo.delete_category")
    def test_update_and_delete_parameterized_by_presence(
        self, delete_category_mock, update_category_mock, get_category_mock
    ):
        scenarios = [
            {"name": "present", "category": object(), "expect_update": True, "expect_delete": True},
            {"name": "missing", "category": None, "expect_update": False, "expect_delete": False},
        ]

        for scenario in scenarios:
            with self.subTest(case=scenario["name"]):
                category = scenario["category"]
                get_category_mock.reset_mock()
                update_category_mock.reset_mock()
                delete_category_mock.reset_mock()
                get_category_mock.return_value = category
                update_category_mock.return_value = object()

                update_out = ProductCategoryService.update(4, {"description": "x"})
                delete_out = ProductCategoryService.delete(1)

                if scenario["expect_update"]:
                    self.assertIs(update_out, update_category_mock.return_value)
                    update_category_mock.assert_called_once_with(category, {"description": "x"})
                else:
                    self.assertIsNone(update_out)
                    update_category_mock.assert_not_called()

                if scenario["expect_delete"]:
                    self.assertTrue(delete_out)
                    delete_category_mock.assert_called_once_with(category)
                else:
                    self.assertFalse(delete_out)
                    delete_category_mock.assert_not_called()

    @patch("products.product_category_service.repo.get_category")
    @patch("products.product_category_service.repo.list_products_by_category")
    def test_list_products_when_category_exists(self, list_by_category_mock, get_category_mock):
        category = object()
        get_category_mock.return_value = category
        list_by_category_mock.return_value = [object()]

        out = ProductCategoryService.list_products(2, include_deleted=True)

        self.assertEqual(out, list_by_category_mock.return_value)
        list_by_category_mock.assert_called_once_with(category, include_deleted=True)

    @patch("products.product_category_service.repo.get_category")
    def test_list_products_when_category_missing(self, get_category_mock):
        get_category_mock.return_value = None
        out = ProductCategoryService.list_products(2)
        self.assertIsNone(out)

    @patch("products.product_category_service.repo.get_category")
    @patch("products.product_category_service.repo.get_products_by_ids")
    @patch("products.product_category_service.repo.assign_products_to_category")
    def test_add_products_parameterized(
        self, assign_mock, get_products_mock, get_category_mock
    ):
        scenarios = [
            {
                "name": "success",
                "category": object(),
                "product_ids": [7, 8],
                "fetched_products": [object(), object()],
                "expect_none": False,
            },
            {
                "name": "missing_some_products",
                "category": object(),
                "product_ids": [7, 8],
                "fetched_products": [object()],
                "expect_none": True,
            },
            {
                "name": "missing_category",
                "category": None,
                "product_ids": [7],
                "fetched_products": [object()],
                "expect_none": True,
            },
        ]
        for scenario in scenarios:
            with self.subTest(case=scenario["name"]):
                get_category_mock.reset_mock()
                get_products_mock.reset_mock()
                assign_mock.reset_mock()
                get_category_mock.return_value = scenario["category"]
                get_products_mock.return_value = scenario["fetched_products"]

                out = ProductCategoryService.add_products(1, scenario["product_ids"])

                if scenario["expect_none"]:
                    self.assertIsNone(out)
                    assign_mock.assert_not_called()
                else:
                    self.assertEqual(out, scenario["fetched_products"])
                    assign_mock.assert_called_once_with(
                        scenario["category"], scenario["fetched_products"]
                    )

    @patch("products.product_category_service.repo.get_category")
    @patch("products.product_category_service.repo.get_products_by_ids")
    @patch("products.product_category_service.repo.remove_products_from_category")
    def test_remove_products_success(self, remove_mock, get_products_mock, get_category_mock):
        category = object()
        p1 = object()
        get_category_mock.return_value = category
        get_products_mock.return_value = [p1]

        out = ProductCategoryService.remove_products(1, [7])

        self.assertEqual(out, [p1])
        remove_mock.assert_called_once_with(category, [p1])
