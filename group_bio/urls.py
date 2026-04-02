from django.urls import path
from . import views

app_name = 'group_bio'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('members/', views.group_members_view, name='members'),
    
    path('edit-theme/', views.edit_theme_view, name='edit_theme'),
    path('reset-theme/', views.reset_theme_view, name='reset_theme'),
    path('theme-preview/', views.theme_preview_view, name='theme_preview'),
    path('theme-history/', views.theme_history_view, name='theme_history'),
]
