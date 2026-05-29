from django.apps import AppConfig
from django.db.models.signals import pre_migrate

def create_content_schema(sender, **kwargs):
    """
    Crea el esquema 'content' en la base de datos (incluyendo la temporal de pruebas)
    justo antes de que Django intente crear las tablas.
    """
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS content;")

class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurants'

    def ready(self):
      
        pre_migrate.connect(create_content_schema, sender=self)