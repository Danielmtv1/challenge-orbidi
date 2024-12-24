# Usa una imagen base oficial de Python
FROM python:3.12

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos al contenedor
COPY requirements.txt /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt
# Copia solo los archivos necesarios para Alembic
COPY alembic.ini /app/

# Copia la carpeta alembic/
COPY alembic/ /app/alembic/ 

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
# Copia todo el código de la aplicación al contenedor
COPY . /app/

# Exponer el puerto en el que corre la app
EXPOSE 8000

# Comando para ejecutar la app con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
