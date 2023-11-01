from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from .models import Messages, Friends
# Create your views here.
from rest_framework import generics
from .serializers import MessageSerializer, FriendsSerializer


class MessageListAPIView(generics.ListCreateAPIView):
    # queryset = Messages.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        result = Messages.objects.filter(sender__id=self.request.user.id,
                                         receiver__id=self.kwargs['friend_id'])
        if result:
            return result
        return

    # def perform_create(self, serializer):
    #     friend_id = self.kwargs['friend_id']
    #     # receiver = Me
    #     friend = User.objects.filter(id=friend_id)
    #     if friend.exists():
    #         serializer.save(sender=self.request.user, receiver=friend.first())
    #     raise ValidationError(detail="Reciver is not found !!!")