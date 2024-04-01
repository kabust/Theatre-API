from rest_framework.pagination import PageNumberPagination


class PerformancePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 20


class ReservationPagination(PageNumberPagination):
    page_size = 1
    max_page_size = 10
