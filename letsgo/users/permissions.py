from rest_framework import permissions

class IsFriendRequestSenderOrReceiver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        print(obj.sender, request.user)
        return obj.sender == request.user or obj.receiver == request.user
        