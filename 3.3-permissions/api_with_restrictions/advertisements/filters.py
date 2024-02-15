from django_filters import rest_framework as filters

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    """Фильтры для объявлений."""

    # TODO: задайте требуемые фильтры

    class Meta:
        model = Advertisement
        fields = ['created_at', 'creator', 'status']
