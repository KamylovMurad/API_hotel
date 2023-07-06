from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Room, Booking


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password = make_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password')


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
          'pk',
          'name',
          'description',
          'price',
          'capacity',
          'type',
          'created_at',
          'is_popular',
        )


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
          'room',
          'start_date',
          'end_date',
        )


class CancelBookingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Booking
        fields = (
          'id',
        )


class MyBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
          'id',
          'room',
          'created_at',
          'start_date',
          'end_date',
          'status'
        ]
