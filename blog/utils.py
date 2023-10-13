from django.db.models import Count, Sum, F

from .models import Post


def filter_posts(query, request, posts):
    if query == 'my_posts':
        posts = posts.filter(author=request.user) \
            if request.user.is_authenticated else posts
    if query == 'popular':
        posts = posts.annotate(likes_quantity=Count(
            'likes')).order_by('-likes_quantity')
    if query == 'new_posts':
        posts = posts.order_by('-date')
    if query == 'favorite':
        posts = posts.filter(favorite=request.user)
    if query == 'liked_posts':
        posts = posts.filter(likes=request.user)
    if query == 'author_post':
        posts = posts.filter(author__pk=request.GET.get('user'))
    if query == 'saved':
        posts = posts.filter(saved=request.user)
    if query == 'views':
        posts = posts.annotate(views_quantity=Count(
            'views')).order_by('-views_quantity')

    if query == 'comments':
        posts = posts.annotate(comments_quantity=Count(
            'comment')).order_by('-comments_quantity')
    if query == 'rate':
        posts = posts.annotate(
            rate=Count('comment') + Count('likes') + Count('views')
        ).order_by('-rate')
    return posts


def do_action(field_name, request, queryset):
    post = Post.objects.get(pk=request.GET.get('pk'))

    if request.user not in queryset.all():
        getattr(post, field_name).add(request.user)
        return
    getattr(post, field_name).remove(request.user)
    return


def filter_comments(request, query, comments):
    if query == 'new':
        comments = comments.order_by('-date')
    elif query == 'old':
        comments = comments.order_by('date')
    elif query == 'popular':
        comments = comments.annotate(likes_quantity=Count(
            'likes')).order_by('-likes_quantity')
    else:
        comments = comments.filter(user=request.user)
    return comments
