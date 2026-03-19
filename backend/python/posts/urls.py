from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name= 'post_list'),
    path('create/', views.create_post, name='create_post'),
    path('get/', views.get_posts),
    path('update/', views.update_post),
    path('delete/', views.delete_post),
]
