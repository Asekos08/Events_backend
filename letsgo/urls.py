from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework_swagger.views import get_swagger_view
from events.views import BookedEventViewSet, EventViewSet, CategoryViewSet, RatingViewSet
from users.views import (
    UserViewSet,
    FriendRequestViewSet,
    FriendViewSet
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,  
)
router = DefaultRouter()
router.register(r"events", EventViewSet)
router.register(r"users", UserViewSet)
router.register(r"friend_requests", FriendRequestViewSet)
router.register(r"friends", FriendViewSet)
router.register(r"booked_events", BookedEventViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"rating", RatingViewSet)


schema_view = get_swagger_view(title='API Documentation')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), ),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(
        url_name="schema"), name="swagger-ui"),  # new
]