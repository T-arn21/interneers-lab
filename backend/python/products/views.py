from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProductCreateSerializer, ProductUpdateSerializer
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


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes"}


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
    """
    Ensures DRF exceptions still return a predictable payload shape.
    """

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

        include_deleted = _parse_bool(request.query_params.get("include_deleted"))
        created_after = _parse_iso_datetime(request.query_params.get("created_after"))
        updated_after = _parse_iso_datetime(request.query_params.get("updated_after"))
        if request.query_params.get("created_after") and created_after is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"created_after": ["Must be a valid ISO 8601 datetime."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.query_params.get("updated_after") and updated_after is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid query params.",
                    "errors": {"updated_after": ["Must be a valid ISO 8601 datetime."]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = ProductService.list_products(
            include_deleted=include_deleted,
            created_after=created_after,
            updated_after=updated_after,
        )
        serialized = [product.to_dict() for product in products]

        paginator = ProductPagination()
        try:
            page = paginator.paginate_queryset(serialized, request, view=self)
        except APIException as exc:
            # E.g. invalid page size/max page size validation from DRF internals.
            raise exc
        return paginator.get_paginated_response(page)


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
        product = ProductService.get_product(product_id, include_deleted=False)
        if not product:
            return Response(
                {
                    "success": False,
                    "message": "Product not found.",
                    "errors": {"product_id": ["No matching active product found."]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

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
