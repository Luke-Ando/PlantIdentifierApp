# urls.py
# Connects links to specific views of the app.

# Imports
from django.urls import path
from .views import ClassifyPlantView, ping

# Returns the ClassifyPlantView as a function to be run when the
# path is requested.
urlpatterns = [
    path("ping/", ping),
    path("classify/", ClassifyPlantView.as_view(), name="classify"),
]
