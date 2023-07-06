import django_filters
from .models import Room


class RoomFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='booking__end_date',
        lookup_expr='lte',
        label='Start_date'
    )
    end_date = django_filters.DateFilter(
        field_name='booking__start_date',
        lookup_expr='gte',
        label='End_date'
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ('price', 'Стоимость'),
            ('capacity', 'Вместимость'),
        ),
    )

    class Meta:
        model = Room
        fields = {
            'price': ['exact', 'gte', 'lte'],
            'capacity': ['exact', 'gte', 'lte'],
        }
