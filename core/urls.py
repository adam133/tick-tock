from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("time/", views.get_time_data, name="time_data"),
    path("set-timezone/", views.set_timezone, name="set_timezone"),
]
