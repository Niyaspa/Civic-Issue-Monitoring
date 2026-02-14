from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.volunteer_register, name='volunteer_register'),
    path('login/', views.volunteer_login, name='volunteer_login'),
    path('dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('resources/add/', views.add_resource, name='add_resource'),
    path('resources/delete/<int:pk>/', views.delete_resource, name='delete_resource'),
    path('assignments/<int:pk>/update/', views.update_assignment_status, name='update_assignment_status'),
]
