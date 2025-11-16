from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Property, PropertyImage
from api.models import Inquiry
from .forms import PropertyForm, InquiryForm

from twilio.rest import Client


# ==========================
# ROOT URL (NO TEMPLATE)
# ==========================
def landing_page(request):
    return JsonResponse({"status": "Backend Running", "message": "OK"})


# ==========================
# PUBLIC PROPERTIES LIST
# ==========================
def public_dashboard(request):
    q = request.GET.get("q")
    price_filter = request.GET.get("price")

    properties = Property.objects.all().order_by("-id")

    if q:
        properties = properties.filter(
            Q(title__icontains=q) |
            Q(location__icontains=q)
        )

    if price_filter == "low":
        properties = properties.order_by("price")
    elif price_filter == "high":
        properties = properties.order_by("-price")

    data = [
        {
            "id": prop.id,
            "title": prop.title,
            "price": prop.price,
            "location": prop.location,
            "sold_out": prop.sold_out,
        }
        for prop in properties
    ]

    return JsonResponse({"properties": data})


# ==========================
# ADMIN DASHBOARD (JSON ONLY)
# ==========================
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    properties = Property.objects.all().order_by("-id")

    data = [
        {
            "id": prop.id,
            "title": prop.title,
            "price": prop.price,
            "location": prop.location,
            "sold_out": prop.sold_out,
        }
        for prop in properties
    ]

    return JsonResponse({"admin_properties": data})


# ==========================
# PROPERTY DETAIL
# ==========================
def property_detail(request, property_id):
    prop = get_object_or_404(Property, id=property_id)

    data = {
        "id": prop.id,
        "title": prop.title,
        "location": prop.location,
        "price": prop.price,
        "description": prop.description,
    }

    return JsonResponse(data)


# ==========================
# CONTACT FORM (JSON ONLY)
# ==========================
def contact(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            return JsonResponse({"status": "success", "msg": "Message sent!"})

        return JsonResponse({"status": "error", "errors": form.errors}, status=400)

    return JsonResponse({"status": "contact-page"})


# ==========================
# WHATSAPP SENDER (UNCHANGED)
# ==========================
def send_whatsapp_message(name, phone, property_title, location):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        from_="whatsapp:+14155238886",
        body=f"New Inquiry!\nName: {name}\nPhone: {phone}\nProperty: {property_title}\nLocation: {location}",
        to=f"whatsapp:{settings.AGENT_WHATSAPP_NUMBER}"
    )

    return message.sid
