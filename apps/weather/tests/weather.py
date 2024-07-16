from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from apps.weather.models import SearchHistory
from apps.weather.views import IndexView


class IndexViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("index")

    @patch("apps.weather.views.IndexView.get_weather_data")
    def test_get_request(self, mock_get_weather_data):
        response = self.client.get(self.url)
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Погодa")
        self.assertIsNone(response.context["weather"])
        self.assertIsNone(response.context["last_city"])

        session = self.client.session
        session["last_city"] = "Tashkent"
        session.save()

        mock_get_weather_data.return_value = {
            "name": "Tashkent",
            "main": {"temp": 25},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 1.5},
        }

        response = self.client.get(self.url)
        print(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["weather"]["name"], "Tashkent")
        self.assertEqual(response.context["weather"]["main"]["temp"], 25)
        self.assertEqual(response.context["last_city"], "Tashkent")

    @patch("apps.weather.views.IndexView.get_weather_data")
    def test_post_request(self, mock_get_weather_data):
        mock_get_weather_data.return_value = {
            "name": "Tashkent",
            "main": {"temp": 25},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 1.5},
        }

        response = self.client.post(self.url, {"city": "Tashkent"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["weather"]["name"], "Tashkent")
        self.assertEqual(response.context["weather"]["main"]["temp"], 25)
        self.assertEqual(self.client.session["last_city"], "Tashkent")

        search_history = SearchHistory.objects.get(city="Tashkent")
        self.assertEqual(search_history.search_count, 1)

        mock_get_weather_data.return_value = None
        response = self.client.post(self.url, {"city": "InvalidCity"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["weather"])
        self.assertEqual(response.context["last_city"], "InvalidCity")

    @patch("apps.weather.views.IndexView.get_coordinates")
    @patch("requests.get")
    def test_get_weather_data(self, mock_requests_get, mock_get_coordinates):
        view = IndexView()

        mock_get_coordinates.return_value = (41.2995, 69.2401)
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            "name": "Tashkent",
            "main": {"temp": 25},
            "weather": [{"description": "clear sky"}],
            "wind": {"speed": 1.5},
        }

        weather_data = view.get_weather_data("Tashkent")
        self.assertEqual(weather_data["name"], "Tashkent")
        self.assertEqual(weather_data["main"]["temp"], 25)

    @patch("requests.get")
    def test_get_coordinates(self, mock_requests_get):
        view = IndexView()

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = [
            {"lat": 41.2995, "lon": 69.2401}
        ]

        coordinates = view.get_coordinates("Tashkent")
        self.assertEqual(coordinates, (41.2995, 69.2401))
