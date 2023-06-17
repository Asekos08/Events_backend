from rest_framework import serializers
from .models import User, FriendRequest

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    # password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'friends')

    
    # def validate(self, attrs):
    #     if attrs.get('password') != attrs.get('password2'):
    #         raise serializers.ValidationError(
    #             {"password": "Password fields didn't match."})
    #     return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user
    

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'receiver', 'sender', 'status',)