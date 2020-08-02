from django.contrib import admin
from django.urls import include, path
from . import views
from django.views.generic import TemplateView
# from main_files.holdem.DQN import *
from .views import table_view

urlpatterns = [
    path('', table_view.as_view(), name="table_view"),
    path('api/game/', views.GameListCreate.as_view() ),
    # path('react/', TemplateView.as_view(template_name='poker/react.html')),
]