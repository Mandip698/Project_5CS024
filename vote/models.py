from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    # is_email_verified = models.BooleanField(default=False)
    name = models.CharField(max_length= 200,null=True, blank=True)
    unique_id = models.CharField(max_length=50, unique=True, null=True, blank=True) 
    
    otp = models.CharField(max_length=6, null=True, blank=True) 
    is_otp_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','unique_id']
    
class Poll(models.Model):


    topic = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)  
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50,null= True, blank = True)
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Options(models.Model):
    poll_id = models.ForeignKey('Poll', on_delete=models.CASCADE)
    option_name = models.CharField(max_length=255)
    manifesto = models.TextField(blank=True, null=True)  #agenda
    email = models.EmailField(blank=True, null=True)
    # votes_count = models.PositiveIntegerField(default=0) 
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class UserVotes(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    poll_id = models.ForeignKey('Poll', on_delete=models.CASCADE)
    option_id = models.ForeignKey('Options', null=True,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # When the vote was cast
    
    created_by = models.CharField(max_length=200)
    updated_by = models.CharField(max_length=200)
    

    