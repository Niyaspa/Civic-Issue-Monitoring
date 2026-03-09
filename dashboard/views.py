from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from complaints.models import Complaint
from volunteer.models import VolunteerProfile, VolunteerAssignment


def _get_official_qs(user):
    """Returns the filtered complaint queryset for an official user."""
    qs = Complaint.objects.all()
    if not user.is_superuser:
        profile = getattr(user, 'officialprofile', None)
        if not profile:
            return Complaint.objects.none(), None
        qs = qs.filter(department=profile.department)
        return qs, profile
    return qs, None


@login_required
def dashboard_home(request):
    qs = Complaint.objects.all()

    # Redirect citizens to their own dashboard
    if not request.user.is_superuser:
        profile = getattr(request.user, 'officialprofile', None)
        if not profile:
            from django.shortcuts import redirect
            return redirect('citizen_dashboard')
        qs = qs.filter(department=profile.department)

    # Calculate stats
    total_complaints = qs.count()
    by_category = {}
    for choice in Complaint.CATEGORY_CHOICES:
        count = qs.filter(category=choice[0]).count()
        by_category[choice[1]] = count

    by_status = {}
    for choice in Complaint.STATUS_CHOICES:
        count = qs.filter(status=choice[0]).count()
        by_status[choice[1]] = count

    context = {
        'total_complaints': total_complaints,
        'by_category': by_category,
        'by_status': by_status,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def complaint_data(request):
    qs = Complaint.objects.all()

    if not request.user.is_superuser:
        try:
            profile = getattr(request.user, 'officialprofile', None)
            if profile:
                qs = qs.filter(department=profile.department)
            else:
                qs = Complaint.objects.none()
        except Exception:
            qs = Complaint.objects.none()

    data = []
    for c in qs:
        if c.latitude and c.longitude:
            data.append({
                'lat': c.latitude,
                'lng': c.longitude,
                'category': c.category,
                'description': c.description[:50] + '...' if len(c.description) > 50 else c.description,
            })
    return JsonResponse({'complaints': data})


@login_required
def complaint_list(request):
    qs = Complaint.objects.all()

    # Apply Official filtering
    if not request.user.is_superuser:
        try:
            profile = getattr(request.user, 'officialprofile', None)
            if profile:
                qs = qs.filter(department=profile.department)
            else:
                qs = Complaint.objects.none()
        except Exception:
            qs = Complaint.objects.none()

    # Grab filter parameters
    category = request.GET.get('category')
    status = request.GET.get('status')
    department_id = request.GET.get('department')
    date_sort = request.GET.get('date', 'desc')

    # Apply filters
    if category and category != 'ALL':
        qs = qs.filter(category=category)
    if status and status != 'ALL':
        qs = qs.filter(status=status)
    if request.user.is_superuser and department_id and department_id != 'ALL':
        qs = qs.filter(department_id=department_id)

    # Apply sorting
    if date_sort == 'asc':
        qs = qs.order_by('created_at')
    else:
        qs = qs.order_by('-created_at')

    context = {
        'complaints': qs,
    }
    if request.user.is_superuser:
        from complaints.models import Department
        context['departments'] = Department.objects.all()

    return render(request, 'dashboard/complaints_list.html', context)


@login_required
def complaint_detail(request, pk):
    from django.shortcuts import get_object_or_404

    if request.user.is_superuser:
        complaint = get_object_or_404(Complaint, pk=pk)
    else:
        try:
            profile = request.user.officialprofile
            complaint = get_object_or_404(Complaint, pk=pk, department=profile.department)
        except:
            return render(request, 'dashboard/error.html', {'message': 'Unauthorized access'})

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_category = request.POST.get('category')

        has_changed = False
        if new_status in dict(Complaint.STATUS_CHOICES):
            complaint.status = new_status
            has_changed = True

        if new_category in dict(Complaint.CATEGORY_CHOICES):
            if complaint.category != new_category:
                complaint.category = new_category
                complaint.is_verified = True
                has_changed = True

        if has_changed:
            complaint.save()

    return render(request, 'dashboard/complaint_detail.html', {'complaint': complaint})


@login_required
def volunteer_management(request):
    """Disaster department officials view to manage volunteers and assign tasks."""
    if not request.user.is_superuser:
        profile = getattr(request.user, 'officialprofile', None)
        if not profile:
            return redirect('citizen_dashboard')
        # Only disaster department can access this
        if 'Disaster' not in profile.department.name and 'KSDMA' not in profile.department.name:
            messages.error(request, "This view is only for Disaster Management department officials.")
            return redirect('dashboard_home')

    # Get all volunteers
    volunteers = VolunteerProfile.objects.prefetch_related('resources', 'assignments').all()

    # Handle assignment creation
    if request.method == 'POST':
        volunteer_id = request.POST.get('volunteer_id')
        complaint_id = request.POST.get('complaint_id')
        notes = request.POST.get('notes', '')

        volunteer = get_object_or_404(VolunteerProfile, pk=volunteer_id)
        complaint = get_object_or_404(Complaint, pk=complaint_id, category='DISASTER')

        VolunteerAssignment.objects.create(
            complaint=complaint,
            volunteer=volunteer,
            assigned_by=request.user,
            notes=notes,
        )
        messages.success(request, f"Task assigned to {volunteer.name} successfully!")
        return redirect('volunteer_management')

    # All disaster complaints for the department
    disaster_complaints = Complaint.objects.filter(category='DISASTER').order_by('-created_at')

    return render(request, 'dashboard/volunteer_management.html', {
        'volunteers': volunteers,
        'disaster_complaints': disaster_complaints,
        'existing_assignments': VolunteerAssignment.objects.select_related(
            'complaint', 'volunteer', 'assigned_by'
        ).order_by('-assigned_at')[:50],
    })

@login_required
def leaderboard(request):
    from django.contrib.auth.models import User
    from django.db.models import Count
    
    top_citizens = User.objects.filter(is_superuser=False).annotate(
        report_count=Count('reported_complaints')
    ).filter(report_count__gt=0).order_by('-report_count')[:50]
    
    leaderboard_data = []
    for rank, citizen in enumerate(top_citizens, 1):
        badges = []
        if citizen.report_count >= 1:
            badges.append({'icon': '🥇', 'name': 'Active Reporter', 'color': 'amber'})
        if citizen.report_count >= 5:
            badges.append({'icon': '🏆', 'name': 'Helpful Citizen', 'color': 'purple'})
            
        leaderboard_data.append({
            'rank': rank,
            'username': citizen.username,
            'report_count': citizen.report_count,
            'badges': badges
        })

    return render(request, 'dashboard/leaderboard.html', {'leaderboard_data': leaderboard_data})

