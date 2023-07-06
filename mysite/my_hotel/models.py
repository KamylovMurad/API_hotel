from django.contrib.auth.models import User
from django.db import models


def room_preview_directory_path(instance: "Room", filename: str) -> str:
    return "rooms/room_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Room(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 8)]
    )
    type = models.CharField(
        choices=[
            ('luxe', 'Luxe'),
            ('economy', 'Economy'),
            ('standard', 'Standard')
        ],
        null=True,
        blank=True
    )
    description = models.TextField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_popular = models.BooleanField(null=True, blank=True, default=False)

    class Meta:
        ordering = ["name", "price"]

    def __str__(self):
        return self.name


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('booked', 'Booked'),
            ('cancelled', 'Cancelled'),
            ('confirmed', 'Confirmed')
        ],
        default='booked',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["room", ]

    def __str__(self):
        return f"Booking for {self.room.name} by {self.user.username}"
