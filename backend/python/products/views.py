import csv
import io
from datetime import datetime
from decimal import Decimal

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .product_category_service import ProductCategoryService
from .repository import CategoryFilterError
from .serializers import (
    CategoryProductsMutationSerializer,
    ProductCategoryCreateSerializer,
    ProductCategoryUpdateSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)
from .service import ProductService


def _parse_iso_datetime(raw: str | None) -> datetime | None:
    if raw is None or not str(raw).strip():
        return None
    value = str(raw).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "Products fetched successfully.",
                "data": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )


class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "Categories fetched successfully.",
                "data": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes"}


def _parse_comma_separated_ints(raw: str | None) -> tuple[list[int] | None, str | None]:
    if raw is None or not str(raw).strip():
        return [], None
    out: list[int] = []
    for part in str(raw).split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit():
            return None, f"Each category id must be a positive integer (got {part!r})."
        out.append(int(part))
    return out, None


def _parse_comma_separated_titles(raw: str | None) -> list[str]:
    if raw is None or not str(raw).strip():
        return []
    return [p.strip() for p in str(raw).split(",") if p.strip()]


def _parse_optional_decimal(qp, key: str) -> tuple[Response | None, Decimal | None]:
    raw = qp.get(key)
    if raw is None or not str(raw).strip():
        return None, None
    try:
        return None, Decimal(str(raw).strip())
    except ValueError:
        return (
            Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {key: ["Must be a valid number."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            ),
            None,
        )


def _parse_optional_int(qp, key: str) -> tuple[Response | None, int | None]:
    raw = qp.get(key)
    if raw is None or not str(raw).strip():
        return None, None
    try:
        return None, int(str(raw).strip(), 10)
    except ValueError:
        return (
            Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {key: ["Must be a valid integer."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            ),
            None,
        )


def _parse_optional_bool(qp, key: str) -> tuple[Response | None, bool | None]:
    raw = qp.get(key)
    if raw is None or not str(raw).strip():
        return None, None
    low = str(raw).strip().lower()
    if low in {"1", "true", "yes"}:
        return None, True
    if low in {"0", "false", "no"}:
        return None, False
    return (
        Response(
            {
                "success": False,
                "message": "Invalid query params.",
                "errors": {key: ["Must be true/false, 1/0, or yes/no."]},
            },
            status=status.HTTP_400_BAD_REQUEST,
        ),
        None,
    )


def _validate_pagination_inputs(request):
    max_page_size = ProductPagination.max_page_size
    for key in ("page", "page_size"):
        raw = request.query_params.get(key)
        if raw is None:
            continue
        if not raw.isdigit() or int(raw) <= 0:
            return Response(
                {
                    "success": False,
                    "message": "Invalid pagination query params.",
                    "errors": {key: [f"{key} must be a positive integer."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if key == "page_size" and int(raw) > max_page_size:
            return Response(
                {
                    "success": False,
                    "message": "Invalid pagination query params.",
                    "errors": {
                        "page_size": [f"page_size must be less than or equal to {max_page_size}."]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    return None


class ProductAPIView(APIView):
    def handle_exception(self, exc):
        if isinstance(exc, APIException):
            detail = getattr(exc, "detail", None)
            if isinstance(detail, dict):
                errors = detail
            elif isinstance(detail, list):
                errors = {"non_field_errors": [str(x) for x in detail]}
            else:
                errors = {"non_field_errors": [str(detail)]}

            message = str(detail) if detail is not None else "Request failed."
            return Response(
                {"success": False, "message": message, "errors": errors},
                status=getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST),
            )
        return super().handle_exception(exc)


class ProductListCreateView(ProductAPIView):
    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for creating product.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = ProductService.create(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Product created successfully.",
                "data": product.to_dict(),
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        pagination_error = _validate_pagination_inputs(request)
        if pagination_error:
            return pagination_error

        qp = request.query_params
        include_deleted = _parse_bool(qp.get("include_deleted"))
        created_after = _parse_iso_datetime(qp.get("created_after"))
        updated_after = _parse_iso_datetime(qp.get("updated_after"))
        created_before = _parse_iso_datetime(qp.get("created_before"))
        updated_before = _parse_iso_datetime(qp.get("updated_before"))
        if qp.get("created_after") and created_after is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"created_after": ["Must be a valid ISO 8601 datetime."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qp.get("updated_after") and updated_after is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"updated_after": ["Must be a valid ISO 8601 datetime."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qp.get("created_before") and created_before is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"created_before": ["Must be a valid ISO 8601 datetime."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qp.get("updated_before") and updated_before is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"updated_before": ["Must be a valid ISO 8601 datetime."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        category_ids, ids_err = _parse_comma_separated_ints(qp.get("category_ids"))
        if ids_err:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"category_ids": [ids_err]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        category_titles = _parse_comma_separated_titles(qp.get("category_titles"))

        err, min_price = _parse_optional_decimal(qp, "min_price")
        if err:
            return err
        err, max_price = _parse_optional_decimal(qp, "max_price")
        if err:
            return err
        if min_price is not None and max_price is not None and min_price > max_price:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"price_range": ["min_price must be less than or equal to max_price."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        err, min_wh = _parse_optional_int(qp, "min_warehouse_qty")
        if err:
            return err
        err, max_wh = _parse_optional_int(qp, "max_warehouse_qty")
        if err:
            return err
        if min_wh is not None and max_wh is not None and min_wh > max_wh:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {
                        "warehouse_qty": [
                            "min_warehouse_qty must be less than or equal to max_warehouse_qty."
                        ]
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        brand = qp.get("brand")
        brand = str(brand).strip() if brand is not None and str(brand).strip() else None
        brand_contains = qp.get("brand_contains")
        brand_contains = (
            str(brand_contains).strip()
            if brand_contains is not None and str(brand_contains).strip()
            else None
        )
        search = qp.get("search")
        search = str(search).strip() if search is not None and str(search).strip() else None

        err, has_category = _parse_optional_bool(qp, "has_category")
        if err:
            return err

        try:
            products_qs = ProductService.list_products(
                include_deleted=include_deleted,
                created_after=created_after,
                updated_after=updated_after,
                created_before=created_before,
                updated_before=updated_before,
                category_ids=category_ids or None,
                category_titles=category_titles or None,
                min_price=min_price,
                max_price=max_price,
                min_warehouse_quantity=min_wh,
                max_warehouse_quantity=max_wh,
                brand=brand,
                brand_icontains=brand_contains,
                search=search,
                has_category=has_category,
            )
        except CategoryFilterError as exc:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"categories": [str(exc)]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        paginator = ProductPagination()
        page = paginator.paginate_queryset(products_qs, request, view=self)
        serialized = [product.to_dict() for product in page]
        return paginator.get_paginated_response(serialized)


class ProductBulkCreateView(ProductAPIView):
    required_columns = [
        "name",
        "description",
        "category_title",
        "price",
        "brand",
        "warehouse_quantity",
    ]

    def post(self, request):
        csv_data = self._read_csv_payload(request)
        if csv_data is None:
            return Response(
                {
                    "success": False,
                    "message": "CSV payload is required.",
                    "errors": {"file": ["Provide text/csv body or multipart file field `file`."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reader = csv.DictReader(io.StringIO(csv_data))
        except Exception:
            return Response(
                {
                    "success": False,
                    "message": "Invalid CSV payload.",
                    "errors": {"file": ["Unable to parse CSV."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reader.fieldnames:
            return Response(
                {
                    "success": False,
                    "message": "Invalid CSV payload.",
                    "errors": {"file": ["CSV headers are required."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        missing = [column for column in self.required_columns if column not in reader.fieldnames]
        if missing:
            return Response(
                {
                    "success": False,
                    "message": "Invalid CSV headers.",
                    "errors": {"headers": [f"Missing required columns: {', '.join(missing)}"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payloads = []
        row_errors = {}
        for index, row in enumerate(reader, start=2):
            payload = {
                "name": row.get("name"),
                "description": row.get("description") or "",
                "category": row.get("category_title"),
                "price": row.get("price"),
                "brand": row.get("brand"),
                "warehouse_quantity": row.get("warehouse_quantity"),
            }
            serializer = ProductCreateSerializer(data=payload)
            if not serializer.is_valid():
                row_errors[f"row_{index}"] = serializer.errors
                continue
            payloads.append(serializer.validated_data)

        if row_errors:
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for bulk create.",
                    "errors": row_errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = ProductService.create_bulk(payloads)
        return Response(
            {
                "success": True,
                "message": "Products created successfully.",
                "data": [product.to_dict() for product in created],
            },
            status=status.HTTP_201_CREATED,
        )

    def _read_csv_payload(self, request) -> str | None:
        upload = request.FILES.get("file")
        if upload is not None:
            return upload.read().decode("utf-8")

        if request.content_type and "text/csv" in request.content_type:
            body = request.body.decode("utf-8")
            return body if body.strip() else None
        return None


class ProductDetailView(ProductAPIView):
    def get(self, request, product_id: int):
        include_deleted = _parse_bool(request.query_params.get("include_deleted"))
        product = ProductService.get_product(product_id, include_deleted=include_deleted)
        if not product:
            return Response(
                {
                    "success": False,
                    "message": "Product not found.",
                    "errors": {"product_id": ["No matching active product found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "message": "Product fetched successfully.",
                "data": product.to_dict(),
            }
        )

    def patch(self, request, product_id: int):
        serializer = ProductUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for updating product.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = ProductService.update(product_id, dict(serializer.validated_data))
        if not updated:
            return Response(
                {
                    "success": False,
                    "message": "Product not found.",
                    "errors": {"product_id": ["No matching active product found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if serializer.validated_data.get("deleted") is True:
            return Response(
                {
                    "success": True,
                    "message": "Product deleted successfully.",
                    "data": updated.to_dict(),
                }
            )

        return Response(
            {
                "success": True,
                "message": "Product updated successfully.",
                "data": updated.to_dict(),
            }
        )

    def delete(self, request, product_id: int):
        deleted = ProductService.soft_delete(product_id)
        if not deleted:
            return Response(
                {
                    "success": False,
                    "message": "Product not found.",
                    "errors": {"product_id": ["No matching active product found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "message": "Product deleted successfully.",
                "data": deleted.to_dict(),
            }
        )


class ProductCategoryListCreateView(ProductAPIView):
    def post(self, request):
        serializer = ProductCategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for creating category.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = ProductCategoryService.create(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Category created successfully.",
                "data": category.to_dict(),
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        pagination_error = _validate_pagination_inputs(request)
        if pagination_error:
            return pagination_error
        categories = [category.to_dict() for category in ProductCategoryService.list_categories()]
        paginator = CategoryPagination()
        page = paginator.paginate_queryset(categories, request, view=self)
        return paginator.get_paginated_response(page)


class ProductCategoryDetailView(ProductAPIView):
    def get(self, request, category_id: int):
        category = ProductCategoryService.get(category_id)
        if not category:
            return Response(
                {
                    "success": False,
                    "message": "Category not found.",
                    "errors": {"category_id": ["No matching category found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "success": True,
                "message": "Category fetched successfully.",
                "data": category.to_dict(),
            }
        )

    def patch(self, request, category_id: int):
        serializer = ProductCategoryUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for updating category.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = ProductCategoryService.update(category_id, serializer.validated_data)
        if not category:
            return Response(
                {
                    "success": False,
                    "message": "Category not found.",
                    "errors": {"category_id": ["No matching category found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "success": True,
                "message": "Category updated successfully.",
                "data": category.to_dict(),
            }
        )

    def delete(self, request, category_id: int):
        deleted = ProductCategoryService.delete(category_id)
        if not deleted:
            return Response(
                {
                    "success": False,
                    "message": "Category not found.",
                    "errors": {"category_id": ["No matching category found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"success": True, "message": "Category deleted successfully.", "data": {}})


class ProductCategoryProductsView(ProductAPIView):
    def get(self, request, category_id: int):
        pagination_error = _validate_pagination_inputs(request)
        if pagination_error:
            return pagination_error
        include_deleted = _parse_bool(request.query_params.get("include_deleted"))
        products_qs = ProductCategoryService.list_products(category_id, include_deleted=include_deleted)
        if products_qs is None:
            return Response(
                {
                    "success": False,
                    "message": "Category not found.",
                    "errors": {"category_id": ["No matching category found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
            
        paginator = ProductPagination()
        page = paginator.paginate_queryset(products_qs, request, view=self)
        serialized = [product.to_dict() for product in page]
        return paginator.get_paginated_response(serialized)

    def post(self, request, category_id: int):
        serializer = CategoryProductsMutationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for adding products to category.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated = ProductCategoryService.add_products(
            category_id,
            serializer.validated_data["product_ids"],
        )
        if updated is None:
            return Response(
                {
                    "success": False,
                    "message": "Category or products not found.",
                    "errors": {"product_ids": ["Ensure category and all active products exist."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "success": True,
                "message": "Products added to category successfully.",
                "data": [product.to_dict() for product in updated],
            }
        )

    def delete(self, request, category_id: int):
        serializer = CategoryProductsMutationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed for removing products from category.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        updated = ProductCategoryService.remove_products(
            category_id,
            serializer.validated_data["product_ids"],
        )
        if updated is None:
            return Response(
                {
                    "success": False,
                    "message": "Category or products not found.",
                    "errors": {"product_ids": ["Ensure category and all active products exist."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "success": True,
                "message": "Products removed from category successfully.",
                "data": [product.to_dict() for product in updated],
            }
        )
