from django.urls import path
from rest_framework import routers

from theatre.views import ActorViewSet

router = routers.DefaultRouter()
router.register("actors", ActorViewSet, basename="actors")

urlpatterns = router.urls

app_name = "theatre"
