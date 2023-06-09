from django.http import HttpResponse
import stripe
from itertools import chain
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cleaner, Booking, Profile, User
from django.contrib.auth.models import auth
from django.contrib.auth.hashers import make_password, check_password


stripe.api_key = "sk_test_51NBJzMHwpWY2djhNIdCJtCqAkgxZfXsrLY58SVh52pI0P5nlnJUUexnKu49sf0iuJkcf6WAqwxubQHh0xkjmILiX00xrbSCF8B"

def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    all_users = User.objects.all()

    return HttpResponse("Hello Geeks")

def home(request):
    # user = request.user
    # user_object = User.objects.get(username=request.user.username)
    # user_profile = Profile.objects.get(user=user_object)
    # cleaners = Cleaner.objects.filter(location=user_profile.location)
    # all_users = User.objects.all()
    # return render(request, 'home.html', {'cleaners': cleaners})
    return render(request, 'home.html')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        location = request.POST['location']
        username_object = User.objects.filter(location__icontains=location)
        
        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


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

@login_required(login_url='signin')
def booked(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        return render(request, 'booked.html', {'booking': booking})
    except Booking.DoesNotExist:
        return redirect('home')

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})
