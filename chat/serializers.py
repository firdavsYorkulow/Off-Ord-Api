from jobs.serializers import UserSerializer
from users.models import User
from .models import Messages, Friends
from rest_framework import serializers


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=False)
    receiver = UserSerializer(read_only=False)

    class Meta:
        model = Messages
        fields = "__all__"
        read_only_fields = ('id', 'sender')


class FriendsSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friend = UserSerializer()

    class Meta:
        model = Friends
        fields = '__all__'
