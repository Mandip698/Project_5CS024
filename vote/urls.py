from django.urls import path
from vote.views import index, dashboard, login_view, vote_poll, verify_otp, logout_view

urlpatterns = [
    path('', index, name="index"),
    path('login_view/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout'),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("dashboard/", dashboard, name="dashboard"),
    path('polls/<int:poll_id>/vote/', vote_poll, name='vote_poll'),
]