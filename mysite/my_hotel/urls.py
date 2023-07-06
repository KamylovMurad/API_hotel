from django.urls import path
from .views import (
  RegisterView,
  LoginView,
  RoomListView,
  CreateBookingView,
  UserBookingsView,
  CancelBookingView,
  LogoutView,
  api_root
)

app_name = "my_hotel"


urlpatterns = [
    path('', api_root, name='api-root'),
    path('available/', RoomListView.as_view(), name='available'),
    path('reserve/', CreateBookingView.as_view(), name='reserve'),
    path('bookings/', UserBookingsView.as_view(), name='user_bookings'),
    path
    (
      'bookings/cancel/',
      CancelBookingView.as_view(),
      name='cancel_booking'
    ),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
