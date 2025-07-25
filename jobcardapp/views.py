import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import JobCard, Complaint, ComplaintImage


# ----------------- LIST -----------------
def jobcard_list(request):
    jobcards = JobCard.objects.prefetch_related('complaints__images').order_by('-created_at')
    return render(request, 'jobcard_list.html', {'jobcards': jobcards})


# ----------------- CREATE -----------------
def jobcard_create(request):
    if request.method == 'POST':
        try:
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
                        description=desc.strip(),
                        notes=notes[i].strip() if i < len(notes) else ''
                    )
                    for img in request.FILES.getlist(f'images-{i}'):
                        ComplaintImage.objects.create(complaint=complaint, image=img)

            messages.success(request, 'Job card created successfully!')
            return redirect('jobcard_list')
        except Exception as e:
            messages.error(request, f'Error creating job card: {str(e)}')

    items = ["Mouse", "Keyboard", "CPU", "Laptop", "Desktop", "Printer", "Monitor", "Other"]
    return render(request, 'jobcard_form.html', {'items': items})


# ----------------- EDIT -----------------
def jobcard_edit(request, pk):
    job = get_object_or_404(JobCard, pk=pk)
    items = ["Mouse", "Keyboard", "CPU", "Laptop", "Desktop", "Printer", "Monitor", "Other"]

    if request.method == 'POST':
        try:
            # ✅ Remove selected existing images FIRST
            removed_image_ids = request.POST.getlist('remove_images')
            if removed_image_ids:
                for img_id in removed_image_ids:
                    try:
                        img = ComplaintImage.objects.get(id=img_id)
                        # Delete the physical file
                        if img.image and os.path.isfile(img.image.path):
                            os.remove(img.image.path)
                        # Delete the database record
                        img.delete()
                        print(f"Deleted image with ID: {img_id}")  # Debug log
                    except ComplaintImage.DoesNotExist:
                        print(f"Image with ID {img_id} not found")  # Debug log
                        continue
                    except Exception as e:
                        print(f"Error deleting image {img_id}: {str(e)}")  # Debug log
                        continue

            # ✅ Remove complaints marked for deletion
            delete_complaint_ids = request.POST.getlist('delete_complaints[]')
            if delete_complaint_ids:
                for comp_id in delete_complaint_ids:
                    try:
                        comp = Complaint.objects.get(id=comp_id, jobcard=job)
                        # Delete all images for this complaint
                        for img in comp.images.all():
                            if img.image and os.path.isfile(img.image.path):
                                os.remove(img.image.path)
                            img.delete()
                        # Delete the complaint
                        comp.delete()
                        print(f"Deleted complaint with ID: {comp_id}")  # Debug log
                    except Complaint.DoesNotExist:
                        print(f"Complaint with ID {comp_id} not found")  # Debug log
                        continue
                    except Exception as e:
                        print(f"Error deleting complaint {comp_id}: {str(e)}")  # Debug log
                        continue

            # ✅ Update jobcard details
            job.customer = request.POST.get('customer', '').strip()
            job.address = request.POST.get('address', '').strip()
            job.phone = request.POST.get('phone', '').strip()
            job.item = request.POST.get('item', '')
            job.serial = request.POST.get('serial', '').strip()
            job.config = request.POST.get('config', '').strip()
            job.notes = request.POST.get('general_notes', '').strip()
            job.save()
            print("Updated jobcard basic details")  # Debug log

            # ✅ Handle complaints and new images
            complaints = request.POST.getlist('complaints[]')
            notes_list = request.POST.getlist('notes[]')
            complaint_ids = request.POST.getlist('complaint_ids[]')
            processed_ids = []

            for i, desc in enumerate(complaints):
                if not desc.strip():
                    continue

                comp_id = complaint_ids[i] if i < len(complaint_ids) else ''
                note = notes_list[i].strip() if i < len(notes_list) else ''

                if comp_id and comp_id.strip():
                    # Update existing complaint
                    try:
                        comp = Complaint.objects.get(id=comp_id, jobcard=job)
                        comp.description = desc.strip()
                        comp.notes = note
                        comp.save()
                        print(f"Updated existing complaint ID: {comp_id}")  # Debug log
                    except Complaint.DoesNotExist:
                        # If complaint doesn't exist, create new one
                        comp = Complaint.objects.create(jobcard=job, description=desc.strip(), notes=note)
                        print(f"Created new complaint (original ID {comp_id} not found): {comp.id}")  # Debug log
                else:
                    # Create new complaint
                    comp = Complaint.objects.create(jobcard=job, description=desc.strip(), notes=note)
                    print(f"Created new complaint: {comp.id}")  # Debug log

                processed_ids.append(comp.id)

                # ✅ Add new images for this complaint
                new_images = request.FILES.getlist(f'images-{i}')
                for img_file in new_images:
                    ComplaintImage.objects.create(complaint=comp, image=img_file)
                    print(f"Added new image to complaint {comp.id}")  # Debug log

            # ✅ Remove any unprocessed complaints (those not in the form)
            unprocessed_complaints = job.complaints.exclude(id__in=processed_ids)
            for unprocessed_comp in unprocessed_complaints:
                # Delete images first
                for img in unprocessed_comp.images.all():
                    if img.image and os.path.isfile(img.image.path):
                        os.remove(img.image.path)
                    img.delete()
                # Delete the complaint
                unprocessed_comp.delete()
                print(f"Removed unprocessed complaint: {unprocessed_comp.id}")  # Debug log

            messages.success(request, 'Job card updated successfully!')
            return redirect('jobcard_list')

        except Exception as e:
            print(f"Error in jobcard_edit: {str(e)}")  # Debug log
            messages.error(request, f'Error updating job card: {str(e)}')

    return render(request, 'jobcard_edit.html', {'job': job, 'items': items})


# ----------------- DELETE -----------------
@require_POST
def delete_jobcard(request, pk):
    try:
        jobcard = get_object_or_404(JobCard, pk=pk)
        
        # Delete all associated images and complaints
        for complaint in jobcard.complaints.all():
            for img in complaint.images.all():
                if img.image and os.path.isfile(img.image.path):
                    os.remove(img.image.path)
                img.delete()
            complaint.delete()
        
        # Delete the jobcard
        jobcard.delete()
        
        return JsonResponse({"success": True, "message": "Job card deleted successfully!"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})