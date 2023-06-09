from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=20)
    class Meta:
        swappable = 'AUTH_USER_MODEL'
    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
    
class Cleaner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    bio = models.TextField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class Booking(models.Model):
    STATUS_CHOICES = (
            ('PENDING', 'Pending'),
            ('PAID', 'Paid'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
            )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Booking {self.id}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
               return f"Review {self.id}"
