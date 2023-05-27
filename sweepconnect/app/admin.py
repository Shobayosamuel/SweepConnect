from django.contrib import admin
from .models import User, Profile, Cleaner, Booking, Review

# Register your models here.
admin.site.register(User)
admin.site.register(Cleaner)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Profile)
