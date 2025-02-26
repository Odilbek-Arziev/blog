from django.shortcuts import render, redirect

from .models import Post, Comment
from django.db.models import Count


def check_auth(func):
    def inner_func(request, **pk):
        if request.user.is_anonymous:
            return redirect('users:sign-in')
        elif 'slug' in pk and request.user != Post.objects.get(slug=pk.get('slug')).author:
            return render(request, 'error.html', {})
        elif 'pk' in pk and request.user != Comment.objects.get(pk=pk.get('pk')).user:
            return render(request, 'error.html', {})
        return func(request, **pk)
    return inner_func


def filter_posts(posts, order_query):
    match order_query:
        case 'new':
            return posts.order_by('-date_created')
        case 'popular':
            return Post.objects.annotate(
                likes_count=Count('likes')
            ).order_by('-likes_count')
        case 'discuss':
            return Post.objects.annotate(
                comment_count=Count('comment')
            ).order_by('-comment_count')
        case _:
            return posts
