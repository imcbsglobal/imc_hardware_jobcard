from django.db import models
import os

class JobCard(models.Model):
    ITEM_CHOICES = [
        ('Mouse', 'Mouse'),
        ('Keyboard', 'Keyboard'),
        ('CPU', 'CPU'),
        ('Laptop', 'Laptop'),
        ('Desktop', 'Desktop'),
        ('Printer', 'Printer'),
        ('Monitor', 'Monitor'),
        ('Other', 'Other'),
    ]
    
    customer = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    item = models.CharField(max_length=50, choices=ITEM_CHOICES)
    serial = models.CharField(max_length=100, blank=True, null=True)
    config = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)  # For general notes
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Job Card"
        verbose_name_plural = "Job Cards"

    def __str__(self):
        return f"#{self.id} - {self.customer} - {self.item}"

    def get_total_complaints(self):
        return self.complaints.count()
    
    def get_total_images(self):
        return sum(complaint.images.count() for complaint in self.complaints.all())

class Complaint(models.Model):
    jobcard = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name="complaints")
    description = models.TextField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def __str__(self):
        return f"Complaint for {self.jobcard.customer}: {self.description[:50]}..."
    
    def get_image_count(self):
        return self.images.count()

class ComplaintImage(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='complaint_images/')

    class Meta:
        verbose_name = "Complaint Image"
        verbose_name_plural = "Complaint Images"

    def __str__(self):
        return f"Image for: {self.complaint.description[:30]}..."
    
    def delete(self, *args, **kwargs):
        # Delete the actual file when the model instance is deleted
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def get_file_size(self):
        if self.image:
            try:
                return self.image.size
            except:
                return 0
        return 0