
echo "Aplicando migraciones del sistema..."
python manage.py migrate --noinput

echo "Creando superusuario automáticamente..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')"

echo "Ejecutando sembrado de datos (Seeding)..."
python manage.py seed_data

echo "Recolectando archivos estáticos para Nginx..."
python manage.py collectstatic --noinput

echo "Iniciando servidor Gunicorn de producción..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3