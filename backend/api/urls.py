from django.urls import path
from .views import ClassifyPlantView

urlpatterns = [
    path("classify/", ClassifyPlantView.as_view(), name="classify"),
]
