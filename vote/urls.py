from django.urls import path
from vote.views import change_password, index, dashboard, login_view, verify_otp, logout_view, resend_otp, vote_poll, submit_vote, forgot_password_request, reset_password_after_otp

urlpatterns = [
    path('', index, name="index"),
    path('login_view/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout'),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("change-password/", change_password, name="change_password"),
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("dashboard/", dashboard, name="dashboard"),
    path('vote_poll/<int:poll_id>/', vote_poll, name='vote_poll'),
    path('poll/vote/', submit_vote, name='submit_vote'),
    path('forgot-password/', forgot_password_request, name='forgot_password_request'),
    path('reset-password-otp/', reset_password_after_otp, name='reset_password_after_otp'),
]