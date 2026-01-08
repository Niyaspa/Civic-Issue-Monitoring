from django.shortcuts import render, redirect
from .forms import ComplaintForm

def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            if request.user.is_authenticated:
                complaint.reporter = request.user
            complaint.save()
            return redirect('complaint_success')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/submit.html', {'form': form})

def complaint_success(request):
    return render(request, 'complaints/success.html')
