from django.urls import path

from apps.weather.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
]
