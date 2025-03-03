FROM python:3.10-slim

WORKDIR /app

# Copiar el requirements.txt desde la raíz del proyecto
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la carpeta de código fuente
COPY src/bff-service/app ./app

# Copiar el archivo .env con la ruta correcta
COPY src/.env .

# Exponer el puerto
EXPOSE 8080

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]