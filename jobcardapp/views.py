from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import JobCard, Complaint, ComplaintImage
import os

def jobcard_list(request):
    jobcards = JobCard.objects.prefetch_related('complaints__images').order_by('-created_at')
    return render(request, 'jobcard_list.html', {'jobcards': jobcards})

def jobcard_create(request):
    if request.method == 'POST':
        customer = request.POST.get('customer', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()

        items = request.POST.getlist('items[]')
        serials = request.POST.getlist('serials[]')
        configs = request.POST.getlist('configs[]')

        for item_index, item in enumerate(items):
            if not item:
                continue

            job = JobCard.objects.create(
                customer=customer,
                address=address,
                phone=phone,
                item=item,
                serial=serials[item_index] if item_index < len(serials) else '',
                config=configs[item_index] if item_index < len(configs) else '',
                notes=''
            )

            complaints = request.POST.getlist(f'complaints-{item_index}[]')
            notes_list = request.POST.getlist(f'notes-{item_index}[]')

            for c_index, desc in enumerate(complaints):
                if desc.strip():
                    note = notes_list[c_index] if c_index < len(notes_list) else ''
                    complaint = Complaint.objects.create(jobcard=job, description=desc.strip(), notes=note.strip())

                    image_field = f'images-{item_index}-{c_index}[]'
                    images = request.FILES.getlist(image_field)

                    for img in images:
                        ComplaintImage.objects.create(complaint=complaint, image=img)

        messages.success(request, "Job card(s) created successfully.")
        return redirect('jobcard_list')

    items = ["Mouse", "Keyboard", "CPU", "Laptop", "Desktop", "Printer", "Monitor", "Other"]
    return render(request, 'jobcard_form.html', {'items': items})

@require_POST
def delete_jobcard(request, pk):
    try:
        jobcard = get_object_or_404(JobCard, pk=pk)
        for complaint in jobcard.complaints.all():
            for image in complaint.images.all():
                if image.image and os.path.isfile(image.image.path):
                    os.remove(image.image.path)
                image.delete()
            complaint.delete()
        jobcard.delete()
        return JsonResponse({"success": True, "message": "Deleted successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

def jobcard_edit(request, pk):
    job = get_object_or_404(JobCard, pk=pk)
    
    if request.method == 'POST':
        job.customer = request.POST.get('customer', '').strip()
        job.address = request.POST.get('address', '').strip()
        job.phone = request.POST.get('phone', '').strip()
        job.save()
        return redirect('jobcard_list')

    return render(request, 'jobcard_edit.html', {'job': job})