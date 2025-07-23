from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import JobCard, Complaint, ComplaintImage
from .forms import JobCardForm, ComplaintForm, ComplaintImageForm
from django.forms import modelformset_factory

# ----------------- JOB CARD LIST -----------------
def jobcard_list(request):
    jobcards = JobCard.objects.prefetch_related('complaints__images').order_by('-created_at')
    return render(request, 'jobcard_list.html', {'jobcards': jobcards})

# ----------------- CREATE JOB CARD -----------------
def jobcard_create(request):
    if request.method == 'POST':
        jobcard = JobCard.objects.create(
            customer=request.POST.get('customer'),
            address=request.POST.get('address'),
            phone=request.POST.get('phone'),
            item=request.POST.get('item'),
            serial=request.POST.get('serial', ''),
            config=request.POST.get('config', ''),
            notes=request.POST.get('general_notes', '')
        )

        complaints = request.POST.getlist('complaints[]')
        notes = request.POST.getlist('notes[]')

        for i, desc in enumerate(complaints):
            if desc.strip():
                complaint = Complaint.objects.create(
                    jobcard=jobcard,
                    description=desc,
                    notes=notes[i] if i < len(notes) else ''
                )

                images = request.FILES.getlist(f'images-{i}')
                for img in images:
                    ComplaintImage.objects.create(complaint=complaint, image=img)

        return redirect('jobcard_list')

    return render(request, 'jobcard_form.html')

# ----------------- EDIT JOB CARD -----------------
def jobcard_edit(request, pk):
    job = get_object_or_404(JobCard, pk=pk)
    items = ["Mouse", "Keyboard", "CPU", "Laptop", "Desktop", "Printer", "Monitor"]

    if request.method == 'POST':
        # Update fields
        job.customer = request.POST.get('customer')
        job.address = request.POST.get('address')
        job.phone = request.POST.get('phone')
        job.item = request.POST.get('item')
        job.serial = request.POST.get('serial', '')
        job.config = request.POST.get('config', '')
        job.notes = request.POST.get('general_notes', '')
        job.save()

        # Complaints update logic (same as before)
        job.complaints.all().delete()
        complaints = request.POST.getlist('complaints[]')
        notes = request.POST.getlist('notes[]')

        for i, desc in enumerate(complaints):
            if desc.strip():
                complaint = Complaint.objects.create(
                    jobcard=job,
                    description=desc,
                    notes=notes[i] if i < len(notes) else ''
                )
                images = request.FILES.getlist(f'images-{i}')
                for img in images:
                    ComplaintImage.objects.create(complaint=complaint, image=img)

        return redirect('jobcard_list')

    return render(request, 'jobcard_edit.html', {'job': job, 'items': items})


# ----------------- AJAX DELETE JOB CARD -----------------
@require_POST
def delete_jobcard(request, pk):
    if request.method == "POST":
        try:
            jobcard = JobCard.objects.get(pk=pk)
            jobcard.delete()
            return JsonResponse({"success": True})
        except JobCard.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})