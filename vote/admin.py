from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin import AdminSite
from .forms import CustomAdminAuthenticationForm
from .models import User

class CustomAdminSite(AdminSite):
    login_form = CustomAdminAuthenticationForm

admin.site = CustomAdminSite()

admin.site.register(User)
