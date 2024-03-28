from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.serializers import PlayDetailSerializer, PlayListSerializer

PLAY_URL = reverse("theatre:plays-list")


def sample_play(**params):
    play = {
        "title": "Test play",
        "description": "sample",
    }
    play.update(params)
    return Play.objects.create(**play)


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "password"
        )
        self.client.force_authenticate(self.user)

        for _ in range(5):
            sample_play()

    def test_list_plays(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), Play.objects.count())

    def test_filter_plays_by_title(self):
        play1 = sample_play(title="Play1")
        play2 = sample_play(title="Filtering")
        play3 = sample_play(title="PlayFiltering")

        res = self.client.get(PLAY_URL, {"title": "filter"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_retrieve_play(self):
        play = sample_play()
        play.genres.add(Genre.objects.create(name="Genre"))
        play.actors.add(
            Actor.objects.create(first_name="John", last_name="Doe")
        )

        res = self.client.get(
            reverse("theatre:plays-detail", args=[play.id])
        )

        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = {
            "title": "New play",
            "description": "Sample"
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_admin@test.com", "password", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.actor = Actor.objects.create(
            first_name="John", last_name="Doe"
        )
        self.genre = Genre.objects.create(name="Genre")

    def test_create_play(self):
        payload = {
            "title": "New play 2",
            "description": "Sample",
            "actors": [self.actor.id],
            "genres": [self.genre.id]
        }
        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        serializer = PlayDetailSerializer(Play.objects.last())
        res.data.pop("actors")
        res.data.pop("genres")
        for key in res.data:
            self.assertEqual(res.data[key], serializer.data[key])
