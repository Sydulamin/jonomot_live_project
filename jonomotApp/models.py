from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from ckeditor.fields import RichTextField


class CustomUser(AbstractUser):
    username = models.CharField(max_length=255, unique=False, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                              null=True, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    points = models.IntegerField(default=0, null=True, blank=True)
    premium_user = models.BooleanField(default=False)
    auth_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class AllData(models.Model):
    
    OPTION_CHOICES = (
        ('image/video', 'image/video'),
        ('text', 'text'),
        ('image2', 'image2'),
    )
    
    
    media1 = models.ImageField(upload_to='media1/', null=True, blank=True)
    media2 = models.ImageField(upload_to='media2/', null=True, blank=True)
    media3 = models.ImageField(upload_to='media3/', null=True, blank=True)
    media4 = models.ImageField(upload_to='media4/', null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    option1 = models.TextField( null=True, blank=True)
    option2 = models.TextField( null=True, blank=True)
    option3 = models.TextField( null=True, blank=True)
    option4 = models.TextField( null=True, blank=True)
    notice = RichTextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    post_type = models.CharField(max_length=15, choices=OPTION_CHOICES, null=True, blank=True)
    is_comments = models.BooleanField(default=False)
    is_poll = models.BooleanField(default=False)
    Share_count = models.IntegerField(default=0, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f'{self.text} - {self.created_at}'



class Reaction(models.Model):
    REACTION_TYPES = (
        ('LIKE', 'Like'),
        ('LOVE', 'Love'),
        ('HAHA', 'Haha'),
        ('WOW', 'Wow'),
        ('SAD', 'Sad'),
        ('ANGRY', 'Angry'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(AllData, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=5, choices=REACTION_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return f'{self.user.username} - {self.reaction_type}'
        return f'{self.ip_address} - {self.reaction_type}'


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(AllData, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # def __str__(self):
    #     return f"Comment by {self.user.username} on {self.post}"


class PollView(models.Model):
    poll = models.ForeignKey(AllData, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True, blank=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return f'Views for Poll {self.poll.id} by User {self.user.username}'



class OptionChoice(models.Model):
    post = models.ForeignKey(AllData, on_delete=models.CASCADE, related_name='option_choices', null=True, blank=True)
    option_selected = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f'{self.option_selected} - {self.created_at}'


class logo(models.Model):
    logo = models.ImageField(upload_to='logo/', null=True, blank=True)
