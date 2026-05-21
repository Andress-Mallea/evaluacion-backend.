from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError

def healthz(request):
    """Endpoint de control de salud operacional para Docker Compose"""
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        return JsonResponse({'status': 'unhealthy', 'database': 'unavailable'}, status=503)
    return JsonResponse({'status': 'healthy', 'database': 'connected'}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz),
]