from django.urls import path
from . import views

urlpatterns = [
    path('', views.file_list, name='file_list'),
    path('upload/', views.file_upload, name='file_upload'),
    path('file/<int:pk>/', views.file_detail, name='file_detail'),
    path('file/<int:pk>/delete/', views.file_delete, name='file_delete'),
    path('file/<int:pk>/status/', views.file_status, name='file_status'),
    path('api/file/<int:pk>/process/', views.process_uploaded_file, name='process_file'),
] 