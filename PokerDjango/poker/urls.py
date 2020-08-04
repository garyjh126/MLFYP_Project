from django.contrib import admin
from django.urls import include, path
from . import views
# from main_files.holdem.DQN import *
from .views import table_view
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'games', views.GameViewSet)

urlpatterns = [
    path('', table_view.as_view(), name="table_view"),
    path('api/', include(router.urls)),
    # path('react/', TemplateView.as_view(template_name='poker/react.html')),
]