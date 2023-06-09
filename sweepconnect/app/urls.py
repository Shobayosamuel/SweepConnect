from django.urls import path
#now import the views.py file into this code
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cleaner/<int:cleaner_id>/book/', views.book_cleaner, name='book_cleaner'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('booked/<int:booking_id>/', views.booked, name='booked'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('/signup', views.signup, name='signup'),
    path('/signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
]
