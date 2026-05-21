FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido
COPY . .

EXPOSE 8000

# El truco: Ejecutamos el sh forzando el formato correcto de Linux
ENTRYPOINT ["sh", "./entrypoint.sh"]