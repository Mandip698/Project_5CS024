from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model using email for authentication,
    with additional fields for avatar and voter ID verification.
    """
    email = models.EmailField(unique=True, null=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    voter_id = models.CharField(max_length=100, unique=True, null=True, blank=True) 
    voter_id_image = models.ImageField(null=True, blank=True, default="card.png")
    change_password = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name', 'voter_id']


class Poll(models.Model):
    """
    Represents a poll/question with multiple options.
    """
    STATUS_CHOICES = [
    ('live', 'Live'),
    ('closed', 'Closed'),
    ('pending', 'Pending'),
    ]
    topic = models.CharField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)  
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='live')
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_updated_by')


class Option(models.Model):
    """
    Represents a single option/choice under a poll.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)


class UserVote(models.Model):
    """
    Records a user's vote for a specific option in a poll.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE) # links the vote to a specific poll
    user = models.ForeignKey(User, on_delete=models.CASCADE) # links the vote to the user who casts it
    option = models.ForeignKey(Option, null=True,on_delete=models.CASCADE) # Links to the specific option the user chose
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # A user can vote only once in each poll.
    class Meta:
        # list of constraints 
        constraints = [
            models.UniqueConstraint(fields=['poll', 'user'], name='unique_vote_per_user_per_poll')
        ]