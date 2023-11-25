"""
WSGI config for FanVers project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "FanVers.settings"

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FanVers.settings')


# application = get_wsgi_application()
