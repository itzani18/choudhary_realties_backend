# realestate_app/models.py
from django.db import models
from django.urls import reverse
import uuid
import os


def property_image_upload(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"  # safe short filename
    return os.path.join("properties", filename)


class Property(models.Model):

    PROPERTY_TYPES = [
        ("House", "House"),
        ("Flat", "Flat"),
        ("Villa", "Villa"),
        ("Office", "Office"),
        ("Shop", "Shop"),
        ("Showroom", "Showroom"),
        ("Plot", "Plot"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)

    # NEW FIELD
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)

    # HOUSE ONLY
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)

    # LAND / PLOT
    plot_area = models.FloatField(null=True, blank=True)

    # OFFICE / COMMERCIAL
    carpet_area = models.FloatField(null=True, blank=True)
    super_builtup_area = models.FloatField(null=True, blank=True)

    date_posted = models.DateTimeField(auto_now_add=True)
    sold_out = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=property_image_upload)

    def __str__(self):
        return f"{self.property.title} Image"

