from django.urls import path
from vote.views import index, dashboard, verify_email, send_verification_email

urlpatterns = [
    path('', index, name="index"),
    path('dashboard/', dashboard, name='dashboard'),
    path('verify/<uidb64>/<token>/', verify_email, name='verify_email'),
    path("send-verification-email/<int:user_id>/", send_verification_email, name="send_verification_email"),
]