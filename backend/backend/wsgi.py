# wsgi.py
# Connects Web Server Gateway Interface for handling web requests.

"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# Imports
import os
from django.core.wsgi import get_wsgi_application

# Sets the default from environment variables from backend/settings.py
# for the values that have not been set by the environment. 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Runs the web request functionality.
application = get_wsgi_application()
