from django.urls import path
from . import views

urlpatterns = [
    path("", views.register, name='register'),
    path("login/", views.login, name='login'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("edit/", views.edit, name='edit'),
    path("analyze/", views.analyze, name='analyze'),
    path('upload/', views.upload, name='upload'),
    path('download/', views.download, name='download')
]