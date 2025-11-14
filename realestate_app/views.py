from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.conf import settings

from .models import Property, PropertyImage
from api.models import Inquiry
from .forms import PropertyForm, InquiryForm

# ============ HOME / LANDING PAGE ============

def landing_page(request):
    featured_props = Property.objects.filter(sold_out=False)[:6]
    return render(request, "realestate_app/landing.html", {
        "featured_props": featured_props
    })


# ============ PUBLIC DASHBOARD (ALL PROPERTIES) ============

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

    return render(request, "realestate_app/public_dashboard.html", {
        "properties": properties
    })


# ============ ADMIN DASHBOARD (ONLY SUPERUSER) ============

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    q = request.GET.get("q")
    properties = Property.objects.all().order_by("-id")

    if q:
        properties = properties.filter(
            Q(title__icontains=q) |
            Q(location__icontains=q)
        )

    return render(request, "realestate_app/admin_dashboard.html", {
        "properties": properties
    })


# ============ ADD PROPERTY ============

@user_passes_test(lambda u: u.is_superuser)
def add_property(request):
    if request.method == "POST":
        form = PropertyForm(request.POST)
        images = request.FILES.getlist("images")

        if form.is_valid():
            prop = form.save()

            for img in images:
                PropertyImage.objects.create(property=prop, image=img)

            messages.success(request, "Property added successfully!")
            return redirect("admin_dashboard")

    else:
        form = PropertyForm()

    return render(request, "realestate_app/add_property.html", {
        "form": form
    })


# ============ EDIT PROPERTY ============

@user_passes_test(lambda u: u.is_superuser)
def edit_property(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    if request.method == "POST":
        form = PropertyForm(request.POST, instance=prop)
        images = request.FILES.getlist("images")

        if form.is_valid():
            form.save()

            for img in images:
                PropertyImage.objects.create(property=prop, image=img)

            messages.success(request, "Property updated successfully!")
            return redirect("admin_dashboard")

    else:
        form = PropertyForm(instance=prop)

    return render(request, "realestate_app/edit_property.html", {
        "form": form,
        "property": prop,
        "images": prop.images.all()
    })


# ============ DELETE PROPERTY ============

@user_passes_test(lambda u: u.is_superuser)
def delete_property(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    if request.method == "POST":
        prop.delete()
        messages.success(request, "Property deleted successfully!")
        return redirect("admin_dashboard")

    return render(request, "realestate_app/delete_confirm.html", {
        "property": prop
    })


# ============ TOGGLE SOLD OUT ============

@user_passes_test(lambda u: u.is_superuser)
def toggle_sold_out(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    prop.sold_out = not prop.sold_out
    prop.save()

    if prop.sold_out:
        messages.success(request, f"{prop.title} marked as SOLD OUT.")
    else:
        messages.success(request, f"{prop.title} marked as AVAILABLE again.")

    return redirect("admin_dashboard")


# ============ PROPERTY DETAIL PAGE ============

def property_detail(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    form = InquiryForm()

    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = prop
            inquiry.save()

            # WhatsApp
            try:
                send_whatsapp_message(
                    inquiry.name,
                    inquiry.phone,
                    prop.title,
                    prop.location
                )
            except:
                pass

            messages.success(request, "Inquiry submitted successfully!")
            return redirect("property_detail", property_id=property_id)

    return render(request, "realestate_app/property_detail.html", {
        "property": prop,
        "form": form
    })


# ============ CONTACT FORM (SEPARATE CONTACT PAGE) ============

def contact(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            messages.success(request, "Message sent successfully!")
            return redirect("landing")

    else:
        form = InquiryForm()

    return render(request, "realestate_app/contact.html", {"form": form})


# ============ AGENT LOGIN ============

def agent_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "realestate_app/agent_login.html")


# ============ LOGOUT ============

def agent_logout(request):
    logout(request)
    return redirect("landing")


# ============ SEND WHATSAPP MESSAGE (Twilio) ============

from twilio.rest import Client

def send_whatsapp_message(name, phone, property_title, location):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        from_="whatsapp:+14155238886",
        body=f"New Inquiry!\nName: {name}\nPhone: {phone}\nProperty: {property_title}\nLocation: {location}",
        to=f"whatsapp:{settings.AGENT_WHATSAPP_NUMBER}"
    )

    return message.sid
