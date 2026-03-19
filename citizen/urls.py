from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('submit-feedback/<int:complaint_id>/', views.submit_feedback, name='submit_feedback'),
]
