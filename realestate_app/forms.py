from django import forms
from .models import Property, PropertyImage
from api.models import Inquiry

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "title",
            "description",
            "price",
            "location",
            "property_type",
            "bedrooms",
            "bathrooms",
            "plot_area",
            "carpet_area",
            "super_builtup_area",
        ]

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # ✅ this allows multi-file uploads

class PropertyImageForm(forms.ModelForm):
    image = forms.ImageField(widget=MultiFileInput(attrs={'multiple': True}))
    
    class Meta:
        model = PropertyImage
        fields = ['image']

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['name', 'phone', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        }
