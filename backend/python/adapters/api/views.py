import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.application.use_cases import GreetUserUseCase
from core.domain.greeting import GreetingService

greeting_service = GreetingService()
use_case = GreetUserUseCase(greeting_service)


# GET API
def greet_view(request):
    first_name = request.GET.get("first_name")
    last_name = request.GET.get("last_name")

    if not first_name and not last_name:
        return JsonResponse({
        "success": False,
        "data": {
            "full_name": ""
        },
        "message": "Both first and last name missing"
    }, status=400)
    
    full_name = use_case.execute(first_name, last_name)

    return JsonResponse({
        "success": True,
        "data": {
            "full_name": full_name
        },
        "message": "User name processed successfully"
    })


# POST API
@csrf_exempt
def greet_post_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST allowed"}, status=405)

    try:
        body = json.loads(request.body)
        first_name = body.get("first_name")
        last_name = body.get("last_name")
    except:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    full_name = use_case.execute(first_name, last_name)

    return JsonResponse({
        "success": True,
        "data": {
            "full_name": full_name
        },
        "message": "User name processed successfully"
    })