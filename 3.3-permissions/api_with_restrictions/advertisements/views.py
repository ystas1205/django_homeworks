from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from advertisements.models import Advertisement, Favorites
from advertisements.serializers import \
    AdvertisementSerializer, FavoritesSerializer

from advertisements.permissions import IsOwnerOrReadOnly

from advertisements.filters import AdvertisementFilter


class HTTPMethod:
    pass


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
            self.get_queryset().filter(creator__id=user_id, status="DRAFT") | (
                self.filter_queryset(
                    self.get_queryset().filter(status="OPEN") |
                    self.filter_queryset(
                        self.get_queryset().filter(status="CLOSED")))))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

        """Получение прав для действий."""

        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]

        return []

    # Возможность добавлять объявления в избранное
    @action(detail=True, methods=['post', 'delete'])
    def favorites(self, request, pk):
        # user = request.user
        adv = Advertisement.objects.get(id=pk)
        favorite_ads = Favorites.objects.filter(featured_ads=pk)
        b = adv.creator
        if not self.request.user.is_authenticated:
            return Response(
                {
                    'message': 'Вы не авторизованы'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user == b:
            return Response(
                {
                    'message': 'Автор объявления не может добавить или удалить'
                               ' своё объявление'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == "POST":
            Favorites.objects.update_or_create(user=request.user,
                                               featured_ads=adv)
            return Response({'status': 'Обьявление добавлено в избранное'})

        if request.method == "DELETE":
            favorite_ads.delete()
            #  Favorites.objects.filter(featured_ads=pk).delete()
            return Response({'status': 'Обьявление удалено из избранных'})

    # Фильтрации по избранным объявлениям.
    @action(detail=False, methods=['get'])
    def filter(self, request):
        queryset = Favorites.objects.filter(user=request.user.id).all()
        serializer = FavoritesSerializer(queryset, many=True)
        return Response(serializer.data)
