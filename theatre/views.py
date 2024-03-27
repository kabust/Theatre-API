from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

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
    ReservationSerializer,
    ReservationListSerializer,
    PlayDetailSerializer
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
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """List movies with filters"""
        genres = self.request.query_params.get("genres")
        actors = self.request.query_params.get("actors")
        title = self.request.query_params.get("title")

        queryset = self.queryset

        if genres:
            genres = self._params_to_ints(genres)
            queryset = queryset.filter(genres__in=genres)

        if actors:
            actors = self._params_to_ints(actors)
            queryset = queryset.filter(actors__in=actors)

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

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
    queryset = (
        Performance.objects.
        select_related("play", "theatre_hall").
        annotate(
            tickets_available=(
                F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        )
    )
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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """List only authenticated user's reservations"""
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
