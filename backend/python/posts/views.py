from django.shortcuts import render


def posts_list(request):
    return render(request, "posts/post_list.html")
