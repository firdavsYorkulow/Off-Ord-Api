
from rest_framework.urlpatterns import path,include
from .views import MessageListAPIView

urlpatterns = [
    path("messages/<uuid:friend_id>/",MessageListAPIView.as_view())
]
