from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from theatre.models import (
    Actor,
    Genre,
    TheatreHall,
    Play,
    Performance,
    Reservation,
    Ticket
)

from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PlayListSerializer,
    ReservationSerializer, TicketSerializer, TicketListSerializer, ReservationListSerializer, PlayDetailSerializer
)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class PerformancePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 20


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.select_related("play", "theatre_hall")
    serializer_class = PerformanceSerializer
    pagination_class = PerformancePagination

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PerformanceListSerializer
        return PerformanceSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 1
    max_page_size = 10


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__theatre_hall", "tickets__performance__play"
    )
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    # def create(self, request, *args, **kwargs):
    #     pass
