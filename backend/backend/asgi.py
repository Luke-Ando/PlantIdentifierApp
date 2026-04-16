# asgi.py
# Asynchronous Serve Gateway Interface connects the application to the asynchronous
# HTTP requests.

"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# Imports
import os
from django.core.asgi import get_asgi_application

# Sets the default from environment variables from backend/settings.py
# for the values that have not been set by the environment. 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Runs the asynchronou web request functionality.
application = get_asgi_application()
