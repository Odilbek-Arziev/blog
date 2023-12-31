from django.shortcuts import render, redirect
from .models import *
from .forms import PostForm, CommentForm
from django.db.models import Q, Prefetch
from django.contrib.auth.decorators import login_required
from .utils import *
from django.core.paginator import Paginator


def home(request):
    posts = Post.objects.all()
    search = request.GET.get('search')
    query = request.GET.get('filter')
    action = request.GET.get('action')

    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    posts = filter_posts(query, request, posts) if query else posts
    posts = posts.filter(
        date__range=[from_date, to_date]) if from_date else posts

    if action:
        favorite_q = Post.objects.get(pk=request.GET.get('pk')).favorite
        do_action(action, request, favorite_q)
        return redirect('blog:home')

    posts = posts.filter(
        Q(title__icontains=search) |
        Q(text__icontains=search)
    ) if search else posts

    pages = Paginator(posts, 1)
    page = request.GET.get('page')
    posts = pages.get_page(page)

    post_pages = posts.paginator.get_elided_page_range(
        posts.number, on_each_side=2, on_ends=1
    )

    return render(request, 'home.html', {'posts': posts, 'query': query, 'post_pages': post_pages})


@login_required(login_url='/users/log_in')
def post(request, slug):
    post_detail = Post.objects.get(slug=slug)
    form = CommentForm(request.POST or None)
    action = request.GET.get('action')
    query = request.GET.get('filter')

    comments = post_detail.comment_set.filter(parent=None)
    comments = filter_comments(request, query, comments)  \
        if query else comments

    comments = Paginator(comments, 2)
    page = request.GET.get('page')
    comments = comments.get_page(page)

    if action:
        do_action(action, request, post_detail.saved)
        return redirect('blog:post', slug=slug)

    if request.user not in post_detail.views.all():
        post_detail.views.add(request.user)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.post = post_detail
        instance.save()
        return redirect('blog:post', slug=slug)
    return render(request, 'post.html', {'post': post_detail, 'form': form, 'comments': comments})


@login_required(login_url='/users/log_in')
def create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        if Post.objects.last():
            instance.slug = request.POST.get(
                'title') + str(Post.objects.last().pk + 1)
        else:
            instance.slug = request.POST.get('title')
        instance.author = request.user
        instance.save()
        return redirect('blog:home')
    return render(request, 'create.html', {'form': form})


@login_required(login_url='/users/log_in')
def edit_post(request, slug):
    post_data = Post.objects.get(slug=slug)

    if request.user != post_data.author:
        return render(request, 'error.html', {'message': 'редактирование', 'object': 'поста'})

    form = PostForm(request.POST or None,
                    request.FILES or None, instance=post_data)

    if form.is_valid():
        form.save()
        return redirect('blog:post', slug=slug)
    return render(request, 'edit_post.html', {'form': form, 'post': post_data})


@login_required(login_url='/users/log_in')
def delete_post(request, slug):
    post_data = Post.objects.get(slug=slug)

    if request.user != post_data.author:
        return render(request, 'error.html', {'message': 'удаление', 'object': 'поста'})

    if request.method == 'POST':
        post_data.delete()
        return redirect('blog:home')
        # После удаления поста нужно перенаправить пользователя на главную страницу
    return render(request, 'delete_post.html', {'post': post_data})


@login_required(login_url='/users/log_in')
def comment_delete(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.user != comment.user:
        return render(request, 'error.html', {'message': 'удаление', 'object': 'комментария'})

    if request.method == 'POST':
        comment.delete()
        if comment.parent:
            return redirect('blog:reply', pk=comment.parent.pk)
        return redirect('blog:post', slug=comment.post.slug)

    return render(request, 'delete_comment.html', {'comment': comment})


@login_required(login_url='/users/log_in')
def comment_edit(request, pk):
    comment = Comment.objects.get(pk=pk)
    form = CommentForm(request.POST or None, instance=comment)

    if request.user != comment.user:
        return render(request, 'error.html', {'message': 'редактирование', 'object': 'комментария'})

    if request.method == 'POST':
        form.save()
        if comment.parent:
            return redirect('blog:reply', pk=comment.parent.pk)
        return redirect('blog:post', slug=comment.post.slug)

    return render(request, 'edit_comment.html', {'comment': comment, 'form': form})


@login_required(login_url='/users/log_in')
def like(request, pk):
    target = request.GET.get('target')
    field_name = request.GET.get('field')

    object = Post.objects.get(pk=pk) \
        if target == 'post' \
        else Comment.objects.get(pk=pk)

    slug = object.slug if target == 'post' else object.post.slug

    if request.user not in getattr(object, field_name).all():
        getattr(object, field_name).add(request.user)
        getattr(object, 'dislikes' if field_name ==
                'likes' else 'likes').remove(request.user)
    else:
        getattr(object, field_name).remove(request.user)

    reply_to = request.GET.get("to")
    if reply_to:
        return redirect('blog:reply', pk=reply_to)
    return redirect('blog:post', slug=slug)

# redirect of delete and edit


def reply(request, pk):
    replies = Comment.objects.filter(parent=pk)
    parent = Comment.objects.get(pk=pk)
    form = CommentForm(request.POST or None)
    reply_pk = request.POST.get('reply_pk')

    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.post = parent.post
        instance.parent = parent

        if reply_pk:
            instance.reply_to = Comment.objects.get(pk=reply_pk)
        instance.save()
        return redirect('blog:reply', pk=pk)
    return render(request, 'reply.html', {'replies': replies, 'form': form, 'parent': parent})
