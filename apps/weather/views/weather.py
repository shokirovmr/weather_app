from django.shortcuts import render
import requests

from django.views import View
from django.http import JsonResponse

from apps.weather.models.weather import SearchHistory


def index(request):
    weather = None
    city = request.POST.get('city')

    if city:
        response = requests.get('https://api.open-meteo.com/v1/forecast', params={
            'q': city,
            'appid': 'your_api_key',
            'units': 'metric'
        })
        if response.status_code == 200:
            weather = response.json()
            request.session['last_city'] = city

    last_city = request.session.get('last_city')

    return render(request, 'weather/index.html', {'weather': weather, 'last_city': last_city})


class IndexView(View):
    def get(self, request):
        last_city = request.session.get('last_city')
        weather = None
        if last_city:
            weather = self.get_weather_data(last_city)
        return render(request, 'weather/index.html', {'weather': weather, 'last_city': last_city})

    def post(self, request):
        city = request.POST.get('city')
        weather = None
        if city:
            weather = self.get_weather_data(city)
            if weather:
                request.session['last_city'] = city
                self.save_search_history(city)
        return render(request, 'weather/index.html', {'weather': weather, 'last_city': city})

    def get_weather_data(self, city):
        response = requests.get('https://api.open-meteo.com/v1/forecast', params={
            'q': city,
            'appid': 'your_api_key',
            'units': 'metric'
        })
        if response.status_code == 200:
            return response.json()
        return None

    def save_search_history(self, city):
        search, created = SearchHistory.objects.get_or_create(city=city)
        search.search_count += 1
        search.save()
