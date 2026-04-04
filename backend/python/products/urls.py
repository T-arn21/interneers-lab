from django.urls import path

from .views import (
    ProductBulkCreateView,
    ProductCategoryDetailView,
    ProductCategoryListCreateView,
    ProductCategoryProductsView,
    ProductDetailView,
    ProductListCreateView,
)

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="products_list_create"),
    path("bulk/", ProductBulkCreateView.as_view(), name="products_bulk_create"),
    path("<int:product_id>/", ProductDetailView.as_view(), name="products_detail"),
    path(
        "categories/",
        ProductCategoryListCreateView.as_view(),
        name="product_categories_list_create",
    ),
    path(
        "categories/<int:category_id>/",
        ProductCategoryDetailView.as_view(),
        name="product_categories_detail",
    ),
    path(
        "categories/<int:category_id>/products/",
        ProductCategoryProductsView.as_view(),
        name="product_categories_products",
    ),
]
