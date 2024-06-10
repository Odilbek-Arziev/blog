from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    slug = models.SlugField(unique=True)
    date = models.DateField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(default='image.jpg', blank=True)
    likes = models.ManyToManyField(User, related_name='likes')
    dislikes = models.ManyToManyField(User, related_name='dislikes')
    comments_allowed = models.BooleanField(default=True)
    saved = models.ManyToManyField(User, related_name='saved_posts')
    views = models.ManyToManyField(User, related_name='post_views')

    def __str__(self):
        return self.title

    def snippet(self):
        return self.text[:20] + '...читать далее'

    def likes_counter(self):
        return self.likes.count()

    def dislikes_counter(self):
        return self.dislikes.count()


class Person(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post} - {self.body[:15]}"
