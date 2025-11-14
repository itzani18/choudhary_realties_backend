from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from realestate_app.models import Property, PropertyImage
from .models import Inquiry 
from .serializers import PropertySerializer, PropertyImageSerializer, PropertyCreateUpdateSerializer, InquirySerializer
from .permissions import IsSuperUser

import os, requests
from django.core.mail import send_mail
import threading

def run_async(func, *args, **kwargs):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()

# ----------------------------------------
# PROPERTY VIEWSET (CREATE/UPDATE = ADMIN)
# ----------------------------------------
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by("-id")

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateUpdateSerializer
        return PropertySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsSuperUser()]
    
    def create(self, request, *args, **kwargs):
        serializer = PropertyCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prop = serializer.save()
        
        # Return full detail including id
        return Response(PropertySerializer(prop).data, status=201)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSuperUser])
    def toggle_sold(self, request, pk=None):
        prop = self.get_object()
        prop.sold_out = not prop.sold_out
        prop.save()
        return Response({"sold_out": prop.sold_out})


# ----------------------------------------
# PROPERTY IMAGE VIEWSET (MULTIPLE UPLOAD)
# ----------------------------------------
class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsSuperUser()]

    def create(self, request, *args, **kwargs):
        print("------- PROPERTY IMAGE UPLOAD START -------")
        print("DATA:", request.data)
        print("FILES:", request.FILES)

        property_id = request.data.get("property")
        files = request.FILES.getlist("images")

        print("PROPERTY ID:", property_id)
        print("FILES COUNT:", len(files))

        if not property_id:
            return Response({"error": "property is required"}, status=400)
        if not files:
            return Response({"error": "No images provided"}, status=400)

        created = []

        for file in files:
            serializer = PropertyImageSerializer(
                data={"property": property_id, "image": file}
            )
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                print("ERROR:", serializer.errors)
                return Response(serializer.errors, status=400)

        print("------- PROPERTY IMAGE UPLOAD END -------")
        return Response(created, status=201)


# ----------------------------------------
# INQUIRY VIEWSET (FINAL ASYNC VERSION)
# ----------------------------------------
class InquiryViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.all().order_by("-created_at")
    serializer_class = InquirySerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsSuperUser()]

    # ------------------------------------
    # ASYNC EMAIL SENDER
    # ------------------------------------
    def send_email_async(self, inquiry):
        try:
            send_mail(
                subject=f"New Inquiry from {inquiry.name}",
                message=(
                    f"Name: {inquiry.name}\n"
                    f"Phone: {inquiry.phone}\n"
                    f"Email: {inquiry.email}\n"
                    f"Location: {inquiry.location}\n"
                    f"Message: {inquiry.message}\n"
                ),
                from_email=os.environ.get("EMAIL_HOST_USER"),
                recipient_list=[os.environ.get("ADMIN_NOTIFICATION_EMAIL")],
                fail_silently=True
            )
        except Exception as e:
            print("EMAIL FAILED:", e)

    # ------------------------------------
    # ASYNC WHATSAPP SENDER
    # ------------------------------------
    def send_whatsapp_async(self, inquiry):
        try:
            TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
            TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
            TWILIO_WHATSAPP = os.environ.get("TWILIO_WHATSAPP_NUMBER")
            ADMIN_WHATSAPP = os.environ.get("ADMIN_WHATSAPP")

            message_text = (
                f"New Inquiry:\n"
                f"Name: {inquiry.name}\n"
                f"Phone: {inquiry.phone}\n"
                f"Email: {inquiry.email}\n"
                f"Location: {inquiry.location}\n"
                f"Message: {inquiry.message}"
            )

            url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
            data = {
                "From": TWILIO_WHATSAPP,
                "To": ADMIN_WHATSAPP,
                "Body": message_text
            }

            requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_TOKEN))
        except Exception as e:
            print("WHATSAPP FAILED:", e)

    # ------------------------------------
    # MAIN CREATE VIEW — NON BLOCKING
    # ------------------------------------
    def create(self, request, *args, **kwargs):
        print("INQUIRY RECEIVED >>> running create()")

        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inquiry = serializer.save()

        print("Validated & Saved to DB")

        # ASYNC TASKS
        print("Starting async email + whatsapp...")
        run_async(self.send_email_async, inquiry)
        run_async(self.send_whatsapp_async, inquiry)

        print("Response returned instantly, background tasks running...")

        return Response(serializer.data, status=status.HTTP_201_CREATED)
