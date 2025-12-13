# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ .

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build


# Stage 2: Build Backend
FROM python:3.11-slim AS backend-build

WORKDIR /app/services

COPY services/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Stage 3: Final Runtime
FROM python:3.11-slim

# Instalar nginx
RUN apt-get update && apt-get install -y nginx curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar frontend compilado
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY frontend/nginx.conf /etc/nginx/nginx.conf

# Copiar backend
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY services /app/services

WORKDIR /app/services

# Copiar archivos del backend
COPY services .

# Exponer puertos
EXPOSE 8080 8000

# Crear script de inicio
RUN echo '#!/bin/bash\n\
nginx &\n\
sleep 2\n\
python create_db.py\n\
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 127.0.0.1:8000 --timeout 120\n\
' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]
