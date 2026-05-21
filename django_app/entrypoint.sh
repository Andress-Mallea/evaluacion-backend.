
echo "Aplicando migraciones del sistema..."
python manage.py migrate --noinput

echo "Creando superusuario automáticamente..."
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@startup.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpass')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    echo "Superusuario creado con éxito."
EOF

echo "Ejecutando sembrado de datos (Seeding)..."
python manage.py seed_data

echo "Recolectando archivos estáticos para Nginx..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn de producción..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3