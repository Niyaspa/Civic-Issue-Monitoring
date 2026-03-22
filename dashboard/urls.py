from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('api/complaints/', views.complaint_data, name='complaint_data'),
    path('list/', views.complaint_list, name='complaint_list'),
    path('complaint/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('volunteers/', views.volunteer_management, name='volunteer_management'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
