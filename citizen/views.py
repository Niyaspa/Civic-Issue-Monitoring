from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignUpForm
from complaints.models import Complaint
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='citizen.backends.EmailBackend')
            messages.success(request, "Registration successful! Welcome to CivicMonitor.")
            return redirect('citizen_dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def citizen_dashboard(request):
    my_complaints = Complaint.objects.filter(reporter=request.user).order_by('-created_at')
    
    stats = {
        'total': my_complaints.count(),
        'pending': my_complaints.exclude(status='RESOLVED').count(),
        'resolved': my_complaints.filter(status='RESOLVED').count(),
    }
    
    badges = []
    if stats['total'] >= 1:
        badges.append({'icon': '🥇', 'name': 'Active Reporter', 'color': 'amber'})
    if stats['total'] >= 5:
        badges.append({'icon': '🏆', 'name': 'Helpful Citizen', 'color': 'purple'})
    
    return render(request, 'citizen/dashboard.html', {
        'complaints': my_complaints,
        'stats': stats,
        'badges': badges
    })

@login_required
def submit_feedback(request, complaint_id):
    if request.method == 'POST':
        complaint = get_object_or_404(Complaint, id=complaint_id, reporter=request.user, status='RESOLVED')
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text')
        
        if rating:
            complaint.rating = int(rating)
            complaint.feedback_text = feedback_text
            complaint.save()
            messages.success(request, "Thank you for your feedback! It helps us improve our services.")
            
    return redirect('citizen_dashboard')
