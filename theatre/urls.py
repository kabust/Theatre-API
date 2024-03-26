from rest_framework import routers

from theatre.views import (
    ActorViewSet,
    GenreViewSet,
    TheatreHallViewSet,
    PlayViewSet,
    PerformanceViewSet
)

router = routers.DefaultRouter()
router.register("actors", ActorViewSet, basename="actors")
router.register("genres", GenreViewSet, basename="genres")
router.register("theatre_halls", TheatreHallViewSet, basename="theatre-halls")
router.register("plays", PlayViewSet, basename="plays")
router.register("performances", PerformanceViewSet, basename="performances")

urlpatterns = router.urls

app_name = "theatre"
