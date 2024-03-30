from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError

from theatre.utils import play_image_file_path


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"{self.name} - {self.capacity} seats"


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(to=Actor, related_name="plays")
    genres = models.ManyToManyField(to=Genre, related_name="plays")
    image = models.ImageField(null=True, upload_to=play_image_file_path)

    @property
    def description_preview(self):
        if len(self.description) > 50:
            return self.description[:50].strip() + "..."
        return self.description

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]


class Performance(models.Model):
    play = models.ForeignKey(
        to=Play, on_delete=models.CASCADE, related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        to=TheatreHall, on_delete=models.CASCADE, related_name="performances"
    )
    show_time = models.DateTimeField()

    def __str__(self):
        return (
            f'{self.play} in "{self.theatre_hall.name}" '
            f'Theatre on {self.show_time.date()}'
        )


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    def __str__(self):
        return f"Reserved at {self.created_at} by {self.user}"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        to=Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        to=Reservation, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, theatre_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(theatre_hall, theatre_hall_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {theatre_hall_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"row: {self.row}, seat: {self.seat}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["performance", "row", "seat"],
                name="performance_row_seat_unique"
            )
        ]
        ordering = ["row", "seat"]
