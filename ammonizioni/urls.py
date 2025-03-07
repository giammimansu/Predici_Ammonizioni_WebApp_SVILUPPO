from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-players/', views.get_players, name='get_players'),
]