from django.contrib import admin

from apps.weather.models import SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ["city", "search_count"]
