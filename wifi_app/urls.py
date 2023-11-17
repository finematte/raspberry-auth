from django.urls import path
from . import views

wifi_app = "wifi_app"

urlpatterns = [
    path("", views.wifi_view, name="wifi_view"),
    path("connect/", views.connect_to_network, name="connect_to_network"),
    path("tryconnect/", views.try_connect, name="try_connect"),
    path("success/<str:ssid>/", views.success_view, name="success_view"),
    path("shutdown_hotspot/", views.shutdown_hotspot, name="shutdown_hotspot"),
]
