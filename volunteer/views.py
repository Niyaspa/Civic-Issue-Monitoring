from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import VolunteerProfile, VolunteerResource, VolunteerAssignment
from .forms import VolunteerSignUpForm, ResourceForm


def volunteer_register(request):
    if request.method == 'POST':
        form = VolunteerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Welcome! You're now registered as a volunteer.")
            return redirect('volunteer_dashboard')
    else:
        form = VolunteerSignUpForm()
    return render(request, 'volunteer/register.html', {'form': form})


def volunteer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'volunteerprofile'):
            login(request, user)
            return redirect('volunteer_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a volunteer account.")
    return render(request, 'volunteer/login.html')


@login_required
def volunteer_dashboard(request):
    try:
        profile = request.user.volunteerprofile
    except VolunteerProfile.DoesNotExist:
        messages.error(request, "You don't have a volunteer profile.")
        return redirect('home')

    resources = profile.resources.all().order_by('resource_type')
    assignments = profile.assignments.select_related('complaint', 'assigned_by').order_by('-assigned_at')

    return render(request, 'volunteer/dashboard.html', {
        'profile': profile,
        'resources': resources,
        'assignments': assignments,
        'resource_form': ResourceForm(),
    })


@login_required
def toggle_availability(request):
    try:
        profile = request.user.volunteerprofile
        profile.is_available = not profile.is_available
        profile.save()
        status = "available" if profile.is_available else "unavailable"
        messages.success(request, f"You are now marked as {status}.")
    except VolunteerProfile.DoesNotExist:
        messages.error(request, "No volunteer profile found.")
    return redirect('volunteer_dashboard')


@login_required
def add_resource(request):
    if request.method == 'POST':
        try:
            profile = request.user.volunteerprofile
        except VolunteerProfile.DoesNotExist:
            return redirect('home')
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.volunteer = profile
            resource.save()
            messages.success(request, "Resource added successfully.")
        else:
            messages.error(request, "Please check your resource details.")
    return redirect('volunteer_dashboard')


@login_required
def delete_resource(request, pk):
    try:
        profile = request.user.volunteerprofile
        resource = get_object_or_404(VolunteerResource, pk=pk, volunteer=profile)
        resource.delete()
        messages.success(request, "Resource removed.")
    except VolunteerProfile.DoesNotExist:
        pass
    return redirect('volunteer_dashboard')


@login_required
def update_assignment_status(request, pk):
    try:
        profile = request.user.volunteerprofile
    except VolunteerProfile.DoesNotExist:
        return redirect('home')

    assignment = get_object_or_404(VolunteerAssignment, pk=pk, volunteer=profile)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        volunteer_notes = request.POST.get('volunteer_notes', '')
        valid = dict(VolunteerAssignment.STATUS_CHOICES)
        if new_status in valid:
            assignment.status = new_status
            assignment.volunteer_notes = volunteer_notes
            assignment.save()
            messages.success(request, f"Assignment status updated to: {valid[new_status]}")
    return redirect('volunteer_dashboard')
