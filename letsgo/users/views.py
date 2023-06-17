from django.db.models import Q
from rest_framework import exceptions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, FriendRequestSerializer
from .models import User, FriendRequest
from .permissions import IsFriendRequestSenderOrReceiver
from drf_spectacular.utils import extend_schema
from .parameters import get_event_list_parameter

@extend_schema(tags=['Users'])
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@extend_schema(tags=['Friend Request'])
class FriendRequestViewSet(ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsFriendRequestSenderOrReceiver]

    def get_queryset(self):
        queryset = self.queryset
        
        section_params = "receiver"
        section_params = self.request.query_params.get('section') if self.request.query_params.get('section') else section_params

        if section_params == 'sender':
                queryset = queryset.filter(sender=self.request.user)
        elif section_params == 'receiver':
                queryset = queryset.filter(receiver=self.request.user)

        return queryset

    @extend_schema(
        parameters= get_event_list_parameter,
        responses={200: FriendRequestSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        sender_id = request.user.id
        receiver_id = data.get('receiver')

        if sender_id == receiver_id:
            return Response({'error': f'Invalid request to yourself'}, status=404)
        
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        if sender.friends.filter(pk=receiver.pk).exists():
            return Response({'error': f'You are already friends'}, status=404)
        
        if self.queryset.filter((Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=sender) & Q(receiver=receiver))).exists():
            return Response({'error': f'You or the person you want to be a friend already made a request'}, status=404)
        
        request.data['sender'] = sender_id
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        sender = instance.sender
        receiver = instance.receiver

        if request.data['status'] == 'accepted':
            sender.friends.add(receiver)
            sender.save()
            
            self.destroy(request, *args, **kwargs)
            return Response({"message": "Friend request have been accepted"})
        
        if request.data['status'] == 'declined':
            self.destroy(request, *args, **kwargs)
            return Response({"message": "Friend request have been declined"})
        
@extend_schema(tags=['Friends'])
class FriendViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ('get', )

    @extend_schema(
        parameters= get_event_list_parameter,
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.request.user.friends.all()
        user_id = self.request.query_params.get('id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                queryset = user.friends.all()
            except (User.DoesNotExist, ValueError):
                raise exceptions.NotFound("{user_id} not found")

        return queryset