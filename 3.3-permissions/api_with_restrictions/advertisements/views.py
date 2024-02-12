from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from advertisements.models import Advertisement
from advertisements.serializers import \
    AdvertisementSerializer

from advertisements.permissions import IsOwnerOrReadOnly

from advertisements.filters import AdvertisementFilter


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""
    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['status', ]
    filterset_class = AdvertisementFilter

    # Пока объявление в черновике, оно показывается только автору объявления,
    # другим пользователям оно недоступно
    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset_open = self.filter_queryset(
            self.get_queryset().filter(status="OPEN"))
        queryset_closed = self.filter_queryset(
            self.get_queryset().filter(status="CLOSED"))
        queryset = (self.filter_queryset(
            self.get_queryset().filter(creator__id=user_id,
                                       status="DRAFT")) | queryset_open |
                    queryset_closed)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]

        return []
