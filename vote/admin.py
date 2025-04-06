from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin import AdminSite
# from .forms import CustomAdminAuthenticationForm
from .models import User, Poll, Options, UserVotes

# class CustomAdminSite(AdminSite):
#     login_form = CustomAdminAuthenticationForm

# admin.site = CustomAdminSite()

admin.site.register(User)
admin.site.register(Poll)
admin.site.register(Options)
admin.site.register(UserVotes)
