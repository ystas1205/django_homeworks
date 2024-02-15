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
        queryset = self.filter_queryset(
            self.get_queryset().filter(creator__id=user_id, status="DRAFT").
            union(
                self.filter_queryset(self.get_queryset().filter(status="OPEN").
                union(self.filter_queryset(
                    self.get_queryset().filter(status="CLOSED"))))))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

        # def list(self, request, *args, **kwargs):
        #     user_id = request.user.id
        #     queryset_open = self.filter_queryset(
        #         self.get_queryset().filter(status="OPEN"))
        #     queryset_closed = self.filter_queryset(
        #         self.get_queryset().filter(status="CLOSED"))
        #     queryset = (self.filter_queryset(
        #         self.get_queryset().filter(creator__id=user_id,
        #                                    status="DRAFT")) | queryset_open |
        #                 queryset_closed)
        #     serializer = self.get_serializer(queryset, many=True)
        #     return Response(serializer.data)

        """Получение прав для действий."""

        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]

        return []

    # @action(detail=True, methods=['post'])
    # def favorites(self, request, pk=None):
    #     user = self.get_object()
    #     a = user

    # serializer = PasswordSerializer(data=request.data)
    # if serializer.is_valid():
    #     user.set_password(serializer.validated_data['password'])
    #     user.save()
    #     return Response({'status': 'password set'})
    # else:
    #     return Response(serializer.errors,
    #                     status=status.HTTP_400_BAD_REQUEST)
