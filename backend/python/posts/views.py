from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Post, Postdb
from .forms import PostForm
from .serializers import PostSerializer
from django.http import JsonResponse

# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all().order_by('-created_date')
#     serializer_class = PostSerializer

def post_list(request):
    return render(request, 'posts/post_list.html', {})

'''
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')   # change later if needed
    else:
        form = PostForm()

    return render(request, 'posts/post_form.html', {'form': form})
'''

''' QUERIES '''
# CREATE
def create_post(request):
    post = Postdb(title="New Post", content="Hello World!", likes=10)
    post.save()
    return JsonResponse({"message": "Post created"})

# READ
def get_posts(request):
    posts = Postdb.objects()
    data = []

    for p in posts:
        data.append({
            "title": p.title,
            "content": p.content,
            "likes": p.likes
        })

    return JsonResponse(data, safe=False)

# UPDATE
def update_post(request):
    post = Postdb.objects(title="New Post").first()
    if post:
        post.likes += 1
        post.save()
    return JsonResponse({"message": "Updated"})

# DELETE
def delete_post(request):
    Postdb.objects(title="New Post").delete()
    return JsonResponse({"message": "Deleted"})