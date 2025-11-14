# api/serializers.py
from rest_framework import serializers
from realestate_app.models import Property, PropertyImage
from api.models import Inquiry
from django.db import transaction

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "property", "image"]


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = "__all__"


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    bedrooms = serializers.IntegerField(required=False, allow_null=True)
    bathrooms = serializers.IntegerField(required=False, allow_null=True)

    plot_area = serializers.FloatField(required=False, allow_null=True)
    carpet_area = serializers.FloatField(required=False, allow_null=True)
    super_builtup_area = serializers.FloatField(required=False, allow_null=True)

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




class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "name", "phone", "email", "location", "message", "created_at"]
        read_only_fields = ["created_at"]
