from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

#  Custom User Model (Extending Django's Default User)
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = None
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    YEAR_CHOICES = [
    ('Y1', 'Year 1'),
    ('Y2', 'Year 2'),
    ('Y3', 'Year 3'),
    ('Y4', 'Year 4'),
    ('Y5', 'Year 5'),
]
    academic_year = models.CharField(max_length=5,choices=YEAR_CHOICES,  null=True, blank=True)

    student_email = models.EmailField(unique=True, null = True)
   
    tribe = models.CharField(max_length=100, null=True, blank=True)
    course = models.CharField(max_length=200, null=True, blank=True)
    student_number = models.IntegerField(null=True, blank=True, unique=True)
    #student_email = models.EmailField(unique=True, null=False, blank = False)
    is_verified = models.BooleanField(default=False)
#email verification
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True) 
    def __str__(self):
        return f"{self.username} ({self.student_number})"


#  Chat Model (Handles User Messages)
class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)


    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.message[:30]}"


#  Report Model (Handles Reports & Blocking)
class Report(models.Model):
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received")
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    

       

    def __str__(self):
        return f"{self.reported_by} reported {self.reported_user}"

