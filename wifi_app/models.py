from django.db import models
from django import forms

class WifiNetwork(models.Model):
    ssid = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class WifiForm(forms.ModelForm):
    class Meta:
        model = WifiNetwork
        fields = ['ssid', 'password']