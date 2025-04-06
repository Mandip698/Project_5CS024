from django.urls import path
from vote.views import home,send_otp_via_email,verify_otp,resend_otp

urlpatterns = [
    path('', home, name="home"),

    path("send-otp/",send_otp_via_email),
    path('verify-otp/',verify_otp),
    path('resend-otp/',resend_otp)
]