from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

class Cleaner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    bio = models.TextField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cleaner = models.ForeignKey(Cleaner, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20)
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
