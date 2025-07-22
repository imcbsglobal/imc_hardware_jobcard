from django import forms
from .models import JobCard, Complaint, ComplaintImage

class JobCardForm(forms.ModelForm):
    class Meta:
        model = JobCard
        fields = ['customer', 'address', 'phone', 'item', 'serial', 'config']
        widgets = {
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'item': forms.TextInput(attrs={'class': 'form-control'}),
            'serial': forms.TextInput(attrs={'class': 'form-control'}),
            'config': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complaint'}),
        }

class ComplaintImageForm(forms.ModelForm):
    class Meta:
        model = ComplaintImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
