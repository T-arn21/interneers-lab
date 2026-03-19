from django.shortcuts import render
from django.utils import timezone

def my_view(request):
    utc_time = timezone.now() 
    ist_time = timezone.localtime(utc_time) 
    return render(request, 'my_template.html', {'current_time': ist_time})
