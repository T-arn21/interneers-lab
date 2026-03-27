from django.urls import path

from .views import ProductDetailView, ProductListCreateView


urlpatterns = [
    path("", ProductListCreateView.as_view(), name="products_list_create"),
    path("<int:product_id>/", ProductDetailView.as_view(), name="products_detail"),
]

