import os
from django.core.wsgi import get_wsgi_application

# Establece el módulo de configuración por defecto para Django [cite: 193]
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()