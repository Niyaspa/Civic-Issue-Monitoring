from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_complaint, name='submit_complaint'),
    path('success/', views.complaint_success, name='complaint_success'),
]
