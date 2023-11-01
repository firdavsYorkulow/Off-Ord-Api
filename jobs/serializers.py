from rest_framework import serializers

from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)

from users.models import User
# from users.serializers import UserSerializer
from .models import Job, CommentModel, JobLike, CommentLike


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'photo')


class PostDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    post_likes_count = serializers.SerializerMethodField('get_post_likes_count')
    post_comments_count = serializers.SerializerMethodField('get_post_comments_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Job
        fields = ('id', 'user', 'pic', 'description',
                  'created_time',
                  # "post_likes",
                  'post_comments_count',
                  'post_likes_count',
                  'me_liked')


    def get_post_likes_count(self, obj):
        return obj.likes.count()

    def get_post_comments_count(self, obj):
        return obj.comments.count()

    def get_me_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            try:
                like = JobLike.objects.get(post=obj, user=request.user)
                if like:
                    return True

            except JobLike.DoesNotExist:
                return False
        return False


class JobSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id',)


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    me_liked = serializers.SerializerMethodField('get_me_liked')
    likes_count = serializers.SerializerMethodField('get_likes_count')
    replies = serializers.SerializerMethodField('get_replies')
    class Meta:
        model = CommentModel
        fields = ('id', 'user', 'body', 'parent', 'created_time',
                  'replies', 'me_liked', 'likes_count')
        read_only_fields = ('id', 'user',)

    def get_replies(self, obj):
        if obj.child.exists():
            serializer = self.__class__(obj.child.all(), many=True,
                                        context=self.context)
            return serializer.data
        return None

    def get_me_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        else:
            return False

    def get_likes_count(self, obj):
        return obj.likes.count()


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ('id', 'user', 'comment')


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = JobLike
        fields = ('id', 'user', 'post')
        extra_kwargs = {
            'post': {'required': False}
        }