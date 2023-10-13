from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('post/<slug>/', views.post, name='post'),
    path('create/', views.create, name='create'),
    path('edit/<slug>/', views.edit_post, name='edit_post'),
    path('delete/<slug>/', views.delete_post, name='delete_post'),
    path('comment_delete/<int:pk>', views.comment_delete, name='comment_delete'),
    path('comment_edit/<int:pk>', views.comment_edit, name='comment_edit'),
    path('like/<int:pk>', views.like, name='like'),
    path('reply/<int:pk>', views.reply, name='reply')
]
