from django.conf import settings
from django.db import models
from django.utils import timezone
from mongoengine import Document, StringField, IntField

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    text = models.TextField()

    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()

class Postdb(Document):
    title = StringField(required=True)
    content = StringField()
    likes = IntField(default=0)