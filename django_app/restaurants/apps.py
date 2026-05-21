from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurants'
    # Esto traduce el título de la sección en el menú del panel de administración [cite: 799-800]
    verbose_name = _('Restaurantes y Reservas')