FROM python:3.10-slim

WORKDIR /app

# Copiar archivos de requerimientos e instalar dependencias
COPY ./src .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Exponer puerto
EXPOSE 8080

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]