from django.urls import path
from .views import (
    get_daily_token,
    start_daily_recording,
    stop_daily_recording
)

urlpatterns = [
    path('interveiw-section/daily/token/', get_daily_token, name='get_daily_token'),
    path('interveiw-section/daily/start_daily_recording/', start_daily_recording, name='start_daily_recording'),
    path('interveiw-section/daily/stop_daily_recording/', stop_daily_recording, name='stop_daily_recording'),
]
