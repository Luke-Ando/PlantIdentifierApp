# apps.py
# Configures definitions for app and runs startup code for the app.

# Imports
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
