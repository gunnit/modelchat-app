from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('MODEL', 'Model'),
        ('FAN', 'Fan'),
    )
    user_type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='FAN')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    # Override the groups and user_permissions fields to fix reverse accessor clashes
    groups = models.ManyToManyField(Group, blank=True, related_name="customuser_set")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="customuser_set")

# Model for storing chat messages
class ChatMessage(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_translated = models.BooleanField(default=False)  # To track if a message was translated
    original_language = models.CharField(max_length=10, blank=True, null=True)  # Store original language code

# Model for the AI-driven persona settings for models
class DigitalPersona(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='digital_persona')
    greeting_message = models.TextField(blank=True, null=True)
    ai_response_tuning = models.JSONField(blank=True, null=True)  # Can store various tuning parameters

# Model for feedback from both models and fans
class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
