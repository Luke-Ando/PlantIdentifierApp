# manage.py
# Controls the function of the Django server. 

# Sets the interpreter of the file to the python environment installed on the
# the system.
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

# File Imports
import os
import sys

# Main Function
def main():
    """Run administrative tasks."""
    # Creates the environment variable for the server based on the
    # sepcificaltion listed in settings.py, while allowing it to be
    # overwritten during production.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    # Tests whether django has been properly installed in the environment.
    try:
        # Imports the Django funtions to execute the server functions.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc # Prints out the original error message for debugging.
    # Runs the command line arguments associated with the running of the file.
    execute_from_command_line(sys.argv)

# Activates the main function only when this file is directly run.
if __name__ == "__main__":
    main()
