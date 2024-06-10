from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name='home'),
    path('post/<slug>', views.post, name='post'),
    path('create/', views.create, name='create'),
    path('delete/<slug>', views.delete_post, name='delete_post'),
    path('edit/<slug>', views.edit_post, name='edit_post'),
    path('like/<slug>', views.like, name='like'),
    path('dislike/<slug>', views.dislike, name='dislike'),
    path('comment_delete/<int:pk>', views.comment_delete, name='comment_delete'),
    path('comment_edit/<int:pk>', views.comment_edit, name='comment_edit'),
    path('comment_like/<int:pk>', views.comment_like, name='comment_like'),
    path('comment_dislike/<int:pk>', views.comment_dislike, name='comment_dislike'),
    path('save/<slug>', views.save, name='save')
]
