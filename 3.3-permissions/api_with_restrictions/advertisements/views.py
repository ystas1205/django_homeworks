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


class DoesNotExist:
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
            self.get_queryset().filter(creator__id=user_id, status="DRAFT")
            | (
                self.filter_queryset(
                    self.get_queryset().filter(status="OPEN") |
                    self.filter_queryset(
                        self.get_queryset().filter(status="CLOSED")))))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update", 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]

        return []

    # Возможность добавлять объявления в избранное
    @action(detail=True, methods=['post', 'delete'])
    def favorites(self, request, pk):
        global user_avd

        if request.method == "POST":
            try:
                adv = Advertisement.objects.get(id=pk)
                user_avd = adv.creator
            except Advertisement.DoesNotExist:
                adv = None

            if adv is None:
                return Response(
                    {
                        'message': 'Такого обявления нет'},
                    status=status.HTTP_404_NOT_FOUND)

            if request.user == user_avd:
                return Response(
                    {
                        'message': 'Автор объявления не может добавить'
                                   ' своё объявление'},
                    status=status.HTTP_400_BAD_REQUEST)

            Favorites.objects.update_or_create(user=request.user,
                                               featured_ads=adv)
            return Response({'status': 'Обьявление добавлено в избранное'},
                            status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            try:
                favorite_ads = Favorites.objects.get(featured_ads=pk)
            except Favorites.DoesNotExist:
                favorite_ads = None

            if favorite_ads is None:
                return Response(
                    {
                        'message': 'Такого обявления нет в избранных'},
                    status=status.HTTP_404_NOT_FOUND)

            favorite_ads.delete()

            return Response({'status': 'Обьявление удалено из избранных'},
                            status=status.HTTP_204_NO_CONTENT)

    # Фильтрации по избранным объявлениям.
    @action(detail=False, methods=['get'])
    def filter(self, request):
        queryset = Favorites.objects.filter(user=request.user.id).all()
        serializer = FavoritesSerializer(queryset, many=True)
        return Response(serializer.data)
