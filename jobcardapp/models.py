from django.db import models

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

    def __str__(self):
        return f"{self.customer} - {self.item}"

class Complaint(models.Model):
    jobcard = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name="complaints")
    description = models.TextField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.description

class ComplaintImage(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='complaint_images/')

    def __str__(self):
        return f"Image for Complaint: {self.complaint.description}"