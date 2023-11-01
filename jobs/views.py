from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView
# Create your views here.
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.custom_pagination import CustomPagination
from .models import Job, WORK_NEED, WORKER_NEED, CommentModel, JobLike
from .serializers import CommentSerializer, PostDetailSerializer, PostLikeSerializer


class AllJobsView(ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostDetailSerializer
    queryset = Job.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def put(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = self.serializer_class(job, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'status': 200,
                'message': "Post updated successfully",
                'data': serializer.data
            }
        )

    def delete(self, request, *args, **kwargs):
        job = self.get_object()
        job.delete()
        return Response(
            {
                'success': True,
                'status': 204,
                'message': "Post deleted successfully",
                # 'data': serializer.data
            }
        )


class WorkJobsView(ListAPIView):
    serializer_class = PostDetailSerializer
    queryset = Job.objects.filter(job_type=WORK_NEED)
    permission_classes = [IsAuthenticatedOrReadOnly]


class WorkerJobsView(ListAPIView):
    serializer_class = PostDetailSerializer
    queryset = Job.objects.filter(job_type=WORKER_NEED)
    permission_classes = [IsAuthenticatedOrReadOnly]


class SearchWorkView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @staticmethod
    def get(request, query):
        works = Job.objects.filter(job_type=WORKER_NEED).filter(name__icontains=query)
        serializer = PostDetailSerializer(works, many=True)
        return Response(serializer.data)


class SearchWorkerView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, query):
        works = Job.objects.filter(job_type=WORK_NEED).filter(name__icontains=query)
        serializer = PostDetailSerializer(works, many=True)
        return Response(serializer.data)


class CommentDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer
    queryset = CommentModel.objects.all()


class PostCommentsView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs['post']
        comments = CommentModel.objects.filter(
            post=post_id)
        return comments

    def perform_create(self, serializer):
        post_id = self.kwargs['post']
        posts = Job.objects.filter(id=post_id)
        if posts.exists():
            serializer.save(user=self.request.user, post=posts.first())
        else:
            raise ValidationError(detail="Post is not found")

class PostLikeCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PostLikeSerializer

    def get_queryset(self):
        post_id = self.kwargs['id']
        print(post_id, '\n' * 8)

        return JobLike.objects.filter(post__id=post_id)

    def perform_create(self, serializer):
        try:
            post_id = self.kwargs['id']
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, post=Job.objects.filter(id=post_id).first())
        except IntegrityError:
            return
