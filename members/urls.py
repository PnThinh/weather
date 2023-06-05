from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather, name='weather'),
    path('weather24/', views.weather24, name='weather24'),
    path('search/', views.search, name='search'),
]