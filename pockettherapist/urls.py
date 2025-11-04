
from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path("a2a/pockettherapist/", include("agent.urls")),
    # optional health
    path("health/", lambda r: JsonResponse({"status": "ok"})),
]
