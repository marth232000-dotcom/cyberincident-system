from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Incident CRUD
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/<int:pk>/', views.incident_detail, name='incident_detail'),
    path('incidents/create/', views.incident_create, name='incident_create'),
    path('incidents/<int:pk>/update/', views.incident_update, name='incident_update'),
    path('incidents/<int:pk>/delete/', views.incident_delete, name='incident_delete'),
    
    # Evidence CRUD
    path('incidents/<int:incident_id>/evidence/upload/', views.evidence_upload, name='evidence_upload'),
    path('evidence/<int:pk>/delete/', views.evidence_delete, name='evidence_delete'),
    
    # Response CRUD
    path('incidents/<int:incident_id>/response/create/', views.response_create, name='response_create'),
    path('response/<int:pk>/update/', views.response_update, name='response_update'),
    path('response/<int:pk>/delete/', views.response_delete, name='response_delete'),
    
    # User Management (Admin only)
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # Admin
    path('admin/', admin.site.urls),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)