from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import index

schema_view = get_schema_view(
    openapi.Info(
        title="Offord Api",
        default_version="v1",
        description="Offord demo Project",
        terms_of_service="demo.com",
        contact=openapi.Contact(email="firdavsyorkulov@gmail.com"),
        license=openapi.License(name="Demo License")
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('jobs/', include('jobs.urls')),
    path('chat/', include('chat.urls')),
    # path('posts/', include('post.urls')),
    path('', index, name="home_page"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-swagger-i'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name="schema-redoc")
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)