from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from rest_framework.routers import DefaultRouter
from posts import views
from adapters.api.views import greet_view, greet_post_view

def hello_world(request):
    # return HttpResponse("This is an updated message!")

    name = request.GET.get("name","World")
    # return JsonResponse({"message": f"Hello, {name}!"})

    return HttpResponse(f"Hello {name}! This is an updated message")

# router =  DefaultRouter()
# router.register(r'posts',views.PostViewSet)

admin.site.site_header = "New Admin"
admin.site.site_title = "New Admin Portal"
admin.site.index_title = "Welcome to New Portal"
urlpatterns = [
    path('',include('posts.urls')),
    path('admin/', admin.site.urls),
    path('hello/', hello_world),
    # path('posts/', include('posts.urls')),
   # path('contact/', views.contact, name="Contact Us")
    path('greet/',greet_view),
    path('greet-post/', greet_post_view), 
]
