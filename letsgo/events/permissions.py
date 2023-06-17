from rest_framework import permissions

from .models import BookedEvent


class IsEventOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
    
class IsBookedEventOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user