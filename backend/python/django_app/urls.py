from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, JsonResponse

def hello_world(request):
    # return HttpResponse("This is an updated message!")

    name = request.GET.get("name","World")
    # return JsonResponse({"message": f"Hello, {name}!"})

    return HttpResponse(f"Hello {name}! This is an updated message")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', hello_world),
]
