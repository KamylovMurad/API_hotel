from typing import List
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .filters import RoomFilter
from .models import Room, Booking
from django.db.models import Q
from .serializers import RoomSerializer, BookingSerializer, \
    MyBookingSerializer, CancelBookingSerializer, UserSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
def api_root(request) -> Response:
    """
    API корневой эндпоинт.
    """
    return Response({
        'register': request.build_absolute_uri(reverse('my_hotel:register')),
        'login': request.build_absolute_uri(reverse('my_hotel:login')),
        'logout': request.build_absolute_uri(reverse('my_hotel:logout')),
        'available rooms': request.build_absolute_uri(reverse('my_hotel:available')),
        'reserve_room': request.build_absolute_uri(reverse('my_hotel:reserve')),
        'my reservation': request.build_absolute_uri(reverse('my_hotel:user_bookings')),
        'cancel reservation': request.build_absolute_uri(reverse('my_hotel:cancel_booking')),
    }
    )


class RegisterView(CreateAPIView):
    """
    Создание нового пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (~IsAuthenticated,)

    def perform_create(self, serializer) -> None:
        user = serializer.save()
        login(self.request, user)

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        password = request.data.get('password')

        try:
            validate_password(password)
        except Exception as e:
            return Response(
                {
                    'status': str(e),
                    'data': None,
                    'details': None,
                 },
                status=400
            )

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                'status': 'success',
                'data': None,
                'details': 'Registration successful'
            }
        )


class LoginView(CreateAPIView):
    """
    Вход пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (~IsAuthenticated,)

    def post(self, request, *args, **kwargs) -> Response:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request=self.request, user=user)
            return Response(
                {
                    'status': 'success',
                    'user': UserSerializer(user).data,
                    'details': None,
                }
            )
        return Response(
            {
                'status': 'error',
                'data': None,
                'details': 'Invalid credentials'
            },
            status=401
        )


class LogoutView(APIView):
    """
    Выход пользователя.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request) -> Response:
        logout(request)
        return Response(
            {
                'status': 'success',
                'data': None,
                'details': 'Logged out successfully'
            }
        )


class UserBookingsView(ListAPIView):
    """
    Получение списка бронирований пользователя.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = MyBookingSerializer

    def get_queryset(self) -> List[dict]:
        user = self.request.user
        return Booking.objects.filter(user=user)


class CancelBookingView(CreateAPIView):
    """
    Отмена бронирования.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = CancelBookingSerializer

    def post(self, request) -> Response:
        pk = request.data.get('id')
        if request.user.is_superuser:
            try:
                booking = Booking.objects.get(id=pk)
            except Booking.DoesNotExist:
                return Response(
                    {
                        'status': 'error',
                        'data': None,
                        'details': 'Указанная бронь не найдена.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            try:
                booking = Booking.objects.get(id=pk, user=request.user)
            except Booking.DoesNotExist:
                return Response(
                    {
                        'status': 'error',
                        'data': None,
                        'details': 'Указанная бронь не найдена.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        if booking.status == 'cancelled':
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'Бронь уже отменена.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if booking.status == 'confirmed':
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'details': 'Нельзя изменить бронь.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()

        return Response(
            {
                'status': 'success',
                'data': None,
                'detail': 'Бронь успешно отменена.'
            },
            status=status.HTTP_200_OK
        )


class CreateBookingView(CreateAPIView):
    """
    Создание бронирования.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookingSerializer

    def post(self, request) -> Response:
        user = request.user
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        room = request.data.get('room')

        if start_date > end_date:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'detail': 'Дата начала должна быть раньше даты окончания.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            room = Room.objects.get(id=room)
            existing_bookings = Booking.objects.filter(
                room=room,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            existing_bookings = existing_bookings.filter(
                Q(status='booked') | Q(status='confirmed')
            )
            if existing_bookings.exists():
                return Response(
                    {
                        'status': 'error',
                        'data': None,
                        'detail': 'Комната уже забронирована на указанные даты.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Room.DoesNotExist:
            return Response(
                {
                    'status': 'error',
                    'data': None,
                    'detail': 'Указанная комната не найдена.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        Booking.objects.create(
            room=room,
            start_date=start_date,
            end_date=end_date,
            user=user
        )

        return Response(
            {
                'status': 'success',
                'data': None,
                'detail': 'Бронь успешно создана.'
            },
            status=status.HTTP_201_CREATED
        )


class RoomListView(ListAPIView):
    """
    Получение списка номеров.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filterset_class = RoomFilter
    ordering = 'price'

    def filter_queryset(self, queryset) -> List[dict]:
        queryset = super().filter_queryset(queryset)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date and end_date:
            queryset = Room.objects.all()
            booked_rooms = Room.objects.filter(
                booking__start_date__lte=end_date,
                booking__end_date__gte=start_date
            )
            booked_rooms = booked_rooms.filter(
                Q(booking__status='booked') | Q(booking__status='confirmed')
            )

            queryset = queryset.exclude(id__in=booked_rooms)

        return queryset
