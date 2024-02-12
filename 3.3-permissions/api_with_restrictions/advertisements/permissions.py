from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Админы могут менять и удалять любые объявления
        if request.method == "GET" or request.user.is_staff:
            return True
        return request.user == obj.creator







