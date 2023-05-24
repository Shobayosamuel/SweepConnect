from django.http import HttpResponse
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cleaner, Booking

stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    return HttpResponse("Hello Geeks")login_required
def home(request):
    user = request.user
    cleaners = Cleaner.objects.filter(location=user.location)
    return render(request, 'home.html', {'cleaners': cleaners})

@login_required
def book_cleaner(request, cleaner_id):
    user = request.user
    try:
        cleaner = Cleaner.objects.get(id=cleaner_id)
        booking = Booking.objects.create(user=user, cleaner=cleaner)
        # Perform any additional logic or actions for the booking
        return redirect('payment', booking_id=booking.id)
    except Cleaner.DoesNotExist:
        return redirect('home')

@login_required
def payment(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)                                    # Perform payment processing logic here
        if request.method == 'POST':
            # Process the payment and update the booking status
            booking.status = 'PAID'
            booking.save()
            return redirect('booked', booking_id=booking.id)
        return render(request, 'payment.html', {'booking': booking})
    except Booking.DoesNotExist:
        return redirect('home')

@login_required
def booked(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        return render(request, 'booked.html', {'booking': booking})
    except Booking.DoesNotExist:
        return redirect('home')
