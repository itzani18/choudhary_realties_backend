from django.urls import path
from . import views

urlpatterns = [

    # Landing
    path("", views.landing_page, name="landing"),

    # Public Dashboard
    path("properties/", views.public_dashboard, name="public_dashboard"),

    # Property Detail
    path("property/<int:property_id>/", views.property_detail, name="property_detail"),

    # Contact
    path("contact/", views.contact, name="contact"),

    # Admin Dashboard
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # CRUD
    path("add-property/", views.add_property, name="add_property"),
    path("edit-property/<int:property_id>/", views.edit_property, name="edit_property"),
    path("delete-property/<int:property_id>/", views.delete_property, name="delete_property"),

    # Sold Toggle
    path("toggle-sold/<int:property_id>/", views.toggle_sold_out, name="toggle_sold_out"),

    # Auth
    path("agent-login/", views.agent_login, name="agent_login"),
    path("logout/", views.agent_logout, name="agent_logout"),

]
