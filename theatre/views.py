from rest_framework import viewsets

from theatre.models import Actor
from theatre.serializers import ActorSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
