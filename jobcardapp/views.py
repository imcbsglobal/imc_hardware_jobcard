from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import JobCard, Complaint, ComplaintImage
from .forms import JobCardForm, ComplaintForm, ComplaintImageForm

def jobcard_list(request):
    jobcards = JobCard.objects.prefetch_related('complaints__images').order_by('-created_at')
    return render(request, 'jobcard_list.html', {'jobcards': jobcards})

def jobcard_create(request):
    if request.method == 'POST':
        # Extract basic job card data
        customer = request.POST.get('customer')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        item = request.POST.get('item')
        serial = request.POST.get('serial', '')
        config = request.POST.get('config', '')
        general_notes = request.POST.get('general_notes', '')
        
        # Create the job card
        jobcard = JobCard.objects.create(
            customer=customer,
            address=address,
            phone=phone,
            item=item,
            serial=serial,
            config=config,
            notes=general_notes
        )
        
        # Handle complaints and images
        complaints = request.POST.getlist('complaints[]')
        notes = request.POST.getlist('notes[]')
        
        for i, complaint_desc in enumerate(complaints):
            if complaint_desc.strip():  # Only create if complaint has content
                complaint = Complaint.objects.create(
                    jobcard=jobcard,
                    description=complaint_desc,
                    notes=notes[i] if i < len(notes) else ''
                )
                
                # Handle images for this complaint
                images_key = f'images[{i}][]'
                if images_key in request.FILES:
                    images = request.FILES.getlist(images_key)
                    for image in images:
                        ComplaintImage.objects.create(
                            complaint=complaint,
                            image=image
                        )
        
        return redirect('jobcard_list')
    
    return render(request, 'jobcard_form.html')

def jobcard_edit(request, pk):
    jobcard = get_object_or_404(JobCard, pk=pk)
    ComplaintFormSet = modelformset_factory(Complaint, form=ComplaintForm, extra=0, can_delete=True)
    ImageFormSet = modelformset_factory(ComplaintImage, form=ComplaintImageForm, extra=0, can_delete=True)

    if request.method == 'POST':
        job_form = JobCardForm(request.POST, instance=jobcard)
        complaint_formset = ComplaintFormSet(request.POST, queryset=jobcard.complaints.all(), prefix='complaints')
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=ComplaintImage.objects.filter(complaint__jobcard=jobcard), prefix='images')

        if job_form.is_valid() and complaint_formset.is_valid() and image_formset.is_valid():
            jobcard = job_form.save()
            complaints = complaint_formset.save(commit=False)
            for obj in complaint_formset.deleted_objects:
                obj.delete()
            for complaint in complaints:
                complaint.jobcard = jobcard
                complaint.save()

            images = image_formset.save(commit=False)
            for obj in image_formset.deleted_objects:
                obj.delete()
            for image in images:
                if not hasattr(image, 'complaint'):
                    # Assign to first complaint if no specific complaint
                    first_complaint = jobcard.complaints.first()
                    if first_complaint:
                        image.complaint = first_complaint
                image.save()

            return redirect('jobcard_list')
    else:
        job_form = JobCardForm(instance=jobcard)
        complaint_formset = ComplaintFormSet(queryset=jobcard.complaints.all(), prefix='complaints')
        image_formset = ImageFormSet(queryset=ComplaintImage.objects.filter(complaint__jobcard=jobcard), prefix='images')

    return render(request, 'jobcard_form.html', {
        'title': 'Edit Job Card',
        'job_form': job_form,
        'complaint_formset': complaint_formset,
        'image_formset': image_formset,
        'jobcard': jobcard
    })

def jobcard_delete(request, pk):
    jobcard = get_object_or_404(JobCard, pk=pk)
    if request.method == 'POST':
        jobcard.delete()
        return redirect('jobcard_list')
    
    # For GET requests, show confirmation page
    return render(request, 'jobcard_confirm_delete.html', {'jobcard': jobcard})