from django.urls import path

from .views import AllJobsView, WorkJobsView, WorkerJobsView, \
    SearchWorkView, SearchWorkerView, JobRetrieveUpdateDeleteView, PostCommentsView, \
    CommentDetailAPIView, PostLikeCreateListAPIView

urlpatterns = [
    path('', AllJobsView.as_view()),
    path('work/', WorkJobsView.as_view()),
    path("likes/<uuid:id>/", PostLikeCreateListAPIView.as_view()),
    path('detail/<uuid:pk>/', JobRetrieveUpdateDeleteView.as_view()),
    path('work/search/<str:query>/', SearchWorkView.as_view()),
    path('worker/', WorkerJobsView.as_view()),
    path('worker/search/<str:query>/', SearchWorkerView.as_view()),
    path('comments/detail/<pk>/', CommentDetailAPIView.as_view()),
    path('comments/<uuid:post>/', PostCommentsView.as_view()),

]
