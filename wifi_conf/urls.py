from django.urls import include, path

urlpatterns = [
    path('', include('wifi_app.urls'))
]
