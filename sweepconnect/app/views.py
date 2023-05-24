from django.http import HttpResponse
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cleaner, Booking

stripe.api_key = "sk_test_51NBJzMHwpWY2djhNIdCJtCqAkgxZfXsrLY58SVh52pI0P5nlnJUUexnKu49sf0iuJkcf6WAqwxubQHh0xkjmILiX00xrbSCF8B"

def index(request):
    return HttpResponse("Hello Geeks")

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
        booking = Booking.objects.get(id=booking_id)
        if request.method == 'POST':
            # Create a payment intent using Stripe API
            payment_intent = stripe.PaymentIntent.create(
                    amount=booking.total_amount,
                    currency='usd',
                    payment_method_types=['card'],
                    receipt_email=request.user.email
            )
            return JsonResponse({'clientSecret': payment_intent.client_secret})
        return render(request, 'payment.html', {'booking': booking})
    except Booking.DoesNotExist:
        return redirect('home')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers['Stripe-Signature']
    try:
        event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
                )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Handle the Stripe webhook event
    if event['type'] == 'payment_intent.succeeded':
        # Update the booking status to 'PAID'
        payment_intent = event['data']['object']
        booking_id = payment_intent.metadata.get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.status = 'PAID'
                booking.save()
            except Booking.DoesNotExist:
                pass
    return JsonResponse({'status': 'success'})

@login_required
def booked(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        return render(request, 'booked.html', {'booking': booking})
    except Booking.DoesNotExist:
        return redirect('home')
