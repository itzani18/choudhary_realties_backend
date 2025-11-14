from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from realestate_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing'),  # 🏠 Landing page at root URL
    path('app/', include('realestate_app.urls')),
    path("api/", include("api.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
