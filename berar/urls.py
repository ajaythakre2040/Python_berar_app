from django.contrib import admin
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static


class TestAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Main test API is working ✅"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/test/", TestAPIView.as_view()),
    path("api/auth_system/", include("auth_system.urls")),
    path("api/ems/", include("ems.urls")),
    path("api/lead/", include("lead.urls")),
    path("api/cms/", include("cms.urls")),
    path("api/dedup/", include("dedup.urls")),
    path("api/code_of_conduct/", include("code_of_conduct.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
