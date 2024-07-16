import requests
from django.shortcuts import render
from django.views import View

from apps.weather.models import SearchHistory

OPEN_WEATHER_API_KEY = "8dad3db309e50de33c8cdefbe69cec74"


class IndexView(View):
    def get(self, request):
        last_city = request.session.get("last_city")
        weather = None
        if last_city:
            weather = self.get_weather_data(last_city)
        return render(
            request, "weather/index.html", {"weather": weather, "last_city": last_city}
        )

    def post(self, request):
        city = request.POST.get("city")
        weather = None
        if city:
            weather = self.get_weather_data(city)
            if weather:
                request.session["last_city"] = city
                self.save_search_history(city)
        return render(
            request, "weather/index.html", {"weather": weather, "last_city": city}
        )

    def get_weather_data(self, city):
        coordinates = self.get_coordinates(city)
        if not coordinates:
            return None

        latitude, longitude = coordinates
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": OPEN_WEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_coordinates(self, city):
        url = f"http://api.openweathermap.org/geo/1.0/direct"
        params = {"q": city, "limit": 1, "appid": OPEN_WEATHER_API_KEY}
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.json():
            location = response.json()[0]
            return location["lat"], location["lon"]
        return None

    def save_search_history(self, city):
        search, created = SearchHistory.objects.get_or_create(city=city)
        search.search_count += 1
        search.save()
