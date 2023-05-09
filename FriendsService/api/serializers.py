from rest_framework import serializers

from .models import User


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("password", "username")


class FriendRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)


class RespondToFriendRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    action = serializers.BooleanField(required=True)
