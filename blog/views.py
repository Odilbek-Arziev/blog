from django.shortcuts import render, redirect, HttpResponse
from .models import *
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from datetime import datetime


@login_required(login_url='/users/log_in')
def home(request):
    search = request.GET.get('search')
    my_posts = request.GET.get('my_posts')
    favorites = request.GET.get('favorites')
    popular = request.GET.get('popular')
    new = request.GET.get('new')
    show_author = request.GET.get('show_author')
    saved = request.GET.get('saved')
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')

    posts = Post.objects.all()

    posts = posts.filter(author=show_author) if show_author else posts
    posts = posts.filter(saved=request.user) if saved else posts
    posts = posts.filter(likes=request.user) if favorites else posts
    posts = posts.filter(author=request.user) if my_posts else posts
    # posts = posts.filter(likes__gte=1) if popular else posts
    posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:3] \
        if popular else posts
    posts = posts.filter(
        date__range=[start_date, end_date]) \
        if start_date and end_date else posts

    posts = posts.order_by('-date')[:3] if new else posts
    posts = posts.filter(likes=request.user) if favorites else posts

    if search:
        posts = Post.objects.filter(
            Q(title__icontains=search) |
            Q(text__icontains=search))

    pages = Paginator(posts, 2)
    page = request.GET.get('page')
    posts = pages.get_page(page)
    return render(request, 'home.html', {'posts': posts})


@login_required(login_url='/users/log_in')
def post(request, slug):
    post_detail = Post.objects.get(slug=slug)
    comments = post_detail.comment_set.annotate(
        like_count=Count('likes')
    ).order_by('-like_count')
    parent_id = request.POST.get('parent_id')
    form = CommentForm(request.POST or None)

    if request.user not in post_detail.views.all():
        post_detail.views.add(request.user)

    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.post = post_detail
        if parent_id:
            instance.parent = post_detail.comment_set.get(pk=parent_id)
        instance.save()
        return redirect('blog:post', slug=slug)
    return render(
        request,
        'post.html',
        {'post': post_detail, 'form': form, 'comments': comments}
    )


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
def delete_post(request, slug):
    post_data = Post.objects.get(slug=slug)

    if post_data.author != request.user:
        return HttpResponse('<h1>404 Error</h1>', status=404, reason='Delete post')

    if request.method == 'POST':
        post_data.delete()
        return redirect('blog:home')
    return render(request, 'delete_post.html', {'post': post_data})


@login_required(login_url='/users/log_in')
def edit_post(request, slug):
    post_data = Post.objects.get(slug=slug)
    form = PostForm(request.POST or None,
                    request.FILES or None,
                    instance=post_data)

    if post_data.author != request.user:
        return render(request, 'error.html', {'edit_post': True})

    if form.is_valid():
        form.save()
        return redirect('blog:post', slug=slug)
    return render(request,
                  'edit_post.html',
                  {'form': form, 'post': post_data})


def like(request, slug):
    post_data = Post.objects.get(slug=slug)

    if request.user not in post_data.likes.all():
        post_data.likes.add(request.user)
        post_data.dislikes.remove(request.user)
    elif request.user in post_data.likes.all():
        post_data.likes.remove(request.user)
    return redirect('blog:post', slug=slug)


def dislike(request, slug):
    post_data = Post.objects.get(slug=slug)

    if request.user not in post_data.dislikes.all():
        post_data.dislikes.add(request.user)
        post_data.likes.remove(request.user)
    elif request.user in post_data.dislikes.all():
        post_data.dislikes.remove(request.user)
    return redirect('blog:post', slug=slug)


def comment_delete(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post', slug=comment.post.slug)
    return render(request, 'comment_delete.html', {'post': comment.post})


def comment_edit(request, pk):
    comment = Comment.objects.get(pk=pk)
    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid() and request.method == "POST":
        form.save()
        return redirect('blog:post', slug=comment.post.slug)
    return render(request,
                  'comment_edit.html',
                  {'form':  form, 'post': comment.post})


def comment_like(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.user not in comment.likes.all():
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)
    elif request.user in comment.likes.all():
        comment.likes.remove(request.user)
    return redirect('blog:post', slug=comment.post.slug)


def comment_dislike(request, pk):
    comment = Comment.objects.get(pk=pk)

    if request.user not in comment.dislikes.all():
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)
    elif request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
    return redirect('blog:post', slug=comment.post.slug)


def save(request, slug):
    post_data = Post.objects.get(slug=slug)

    post_data.saved.add(request.user) \
        if request.user not in post_data.saved.all() \
        else post_data.saved.remove(request.user)
    return redirect('blog:post', slug=post_data.slug)
