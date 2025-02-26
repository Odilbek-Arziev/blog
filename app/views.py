from django.shortcuts import render, redirect
from .models import Post, Photo
from django.http import HttpResponseNotFound
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .utils import *
from django.core.paginator import Paginator

def get_search(request):
    search_value = request.POST.get("search")

    # Сохранить запрос поиска после срабатывания пагинации

    posts = Post.objects.filter(Q(title__startswith=search_value))
    return render(request, "index.html", {"posts": posts})


def index(request):
    posts = Post.objects.all()
    print(posts)
    posts = filter_posts(posts, request.GET.get('order_by'))
    posts = Post.objects.all()
    pages = Paginator(posts, 2)
    page = request.GET.get('page')
    posts = pages.get_page(page)
    context = {
        "posts": posts,
        "title": "Главная страница",
    }
    return render(request, "index.html", context)


def about(request):
    context = {"title": "О компании"}
    return render(request, "about.html", context)


def contacts(request):
    context = {"title": "Контакты"}
    return render(request, "contacts.html", context)


def post_detail(request, slug):
    post = Post.objects.filter(slug=slug)
    form = CommentForm(request.POST or None)
    parent_id = request.POST.get("parent_id")
    comments = post[0].comment_set.filter(first_comment=None)
    pages = Paginator(comments, 3)
    page = request.GET.get('page')
    comments = pages.get_page(page)

    if request.user not in post[0].views.all():
        post[0].views.add(request.user)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.post = post[0]

        if parent_id:
            main_comment = post[0].comment_set.get(pk=parent_id)
            instance.parent = main_comment

            if not main_comment.first_comment:
                instance.first_comment = main_comment
            else:
                instance.first_comment = main_comment.first_comment

        instance.save()
        return redirect("app:post", slug=slug)

    if not post:
        return HttpResponseNotFound("Такой страницы не существует")
    post = post[0]
  
    context = {"post": post, "form": form, "comments": comments}
    return render(request, "post.html", context)

@check_auth
def post_create(request):
    post_form = PostForm(request.POST)

    if request.method == "POST" and post_form.is_valid():
        images = request.FILES.getlist("images")

        instance = post_form.save(commit=False)
        instance.author = request.user
        instance.save()

        if images:
            for image in images:
                Photo.objects.create(post=instance, image=image)
        else:
            Photo.objects.create(post=instance)

        return redirect("app:index")

    post_form = PostForm()
    return render(request, "post_create.html", {"post_form": post_form, 'title': 'Создание поста'})


@login_required(login_url='/users/sign_in')
def like(request):
    model = request.GET.get("model")
    action = request.GET.get("action")
    value = request.GET.get("value")

    if model == "post":
        object = Post.objects.get(slug=value)
    else:
        object = Comment.objects.get(pk=value)

    user = request.user

    if action == "like":
        if user not in object.likes.all():
            object.likes.add(user)
            object.dislikes.remove(user)
        elif user in object.likes.all():
            object.likes.remove(user)
    else:
        if user not in object.dislikes.all():
            object.dislikes.add(user)
            object.likes.remove(user)
        elif user in object.dislikes.all():
            object.dislikes.remove(user)

    slug = object.slug if not value.isdigit() else object.post.slug
    return redirect("app:post", slug=slug)


@check_auth
def delete_post(request, slug):
    post = Post.objects.get(slug=slug)

    if request.method == "POST":
        post.delete()
        return redirect("app:index")
    return render(request, "delete_post.html", {"post": post})


@check_auth
def edit_post(request, slug):
    post = Post.objects.get(slug=slug)

    post_form = PostForm(request.POST or None,
                         request.FILES or None, instance=post)

    if post_form.is_valid():
        post_form.save()
        return redirect('app:post', slug=request.POST.get('slug'))
    return render(request, 'post_create.html', {'post_form': post_form, 'title': 'Редактирование поста'})


@check_auth
def comment_edit(request, pk):
    comment = Comment.objects.get(pk=pk)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('app:post', slug=comment.post.slug)
    return render(request, 'comment_edit.html', {'form': form})


@check_auth
def comment_delete(request, pk):
    comment = Comment.objects.get(pk=pk)
    post = comment.post.slug
    if request.method == "POST":
        comment.delete()
        return redirect("app:post", slug=post)
    return render(request, 'delete_comment.html', {'slug': post})
