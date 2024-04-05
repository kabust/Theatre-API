from drf_spectacular.utils import OpenApiParameter


PLAY_EXTEND_SCHEMA = [
    OpenApiParameter(
        "actors",
        type={"type": "list", "items": {"type": "number"}},
        description="Filter by Actors IDs… (ex. ?actors=1,3)",
        required=False,
    ),
    OpenApiParameter(
        "genres",
        type={"type": "list", "items": {"type": "number"}},
        description="Filter by Genres IDs… (ex. ?genres=2,5)",
        required=False,
    ),
    OpenApiParameter(
        "title",
        type=str,
        description="Filter by Title…",
        required=False,
    ),
]
