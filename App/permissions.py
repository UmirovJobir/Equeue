from rest_framework import permissions
from . models import *


class IsBusinessCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the creator of a business to add services to it.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self._is_creator(request, view)
    
    def _is_creator(self, request, view):
        # Retrieve the business object
        business_pk = view.kwargs.get('business_pk')
        if business_pk:
            try:
                business = Business.objects.get(pk=business_pk)
            except Business.DoesNotExist:
                return False
            return business.creator == request.user
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.business.creator == request.user