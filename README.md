# Challenge Orbidi

Este proyecto es una aplicación web que utiliza FastAPI y SQLAlchemy para gestionar categorías, ubicaciones y recomendaciones. La arquitectura del proyecto sigue un patrón de diseño modular y limpio para facilitar el mantenimiento y la escalabilidad.

## Tabla de Contenidos

- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Licencia](#licencia)

## Instalación

### Requisitos Previos

- Python 3.10+
- Docker (opcional, para despliegue con Docker)


### Clonar el Repositorio

```bash
git clone https://github.com/Danielmtv1/challenge-orbidi.git
cd challenge-orbidi
```
### Crear y Activar un Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
### Instalar Dependencias
```bash
pip install -r requirements.txt
```
### Configurar la Base de Datos
Configura tu base de datos en el archivo alembic.ini y luego aplica las migraciones
```
alembic upgrade head
```
### Despliegue con Docker (Recomendado)
Para construir las imagenes
```bash
docker-compose up --build
```
tu ahora puedes ingresar a la url ;
```bash
http://0.0.0.0:8000/docs
```
## Uso
### Ejecutar la aplicación
```bash
uvicorn main:app --reload
```

A diferencia del docker en este caso la app estará disponible en http://127.0.0.1:8000/docs

Para comenzar a interactuar con la API, sigue los siguientes pasos, que incluyen la creación de categorías, ubicación y exploración de recomendaciones:

##### 1. Crear Categorías
Primero, es necesario crear una o varias categorías para organizar las ubicaciones. Puedes hacerlo mediante el siguiente endpoint:
**POST /api/v1/categories/**
**Descripción:** 
Crea una o varias categorías. Asegúrate de definir correctamente los parámetros necesarios en el cuerpo de la solicitud.
##### 2. Obtener Categorías
Una vez creadas las categorías, puedes obtener una lista de todas las categorías disponibles con el siguiente endpoint:

**GET /api/v1/categories/**
**Descripción:**
Este endpoint devuelve una lista de todas las categorías que han sido creadas en el sistema.
##### 3. Obtener un ID de Categoría para Crear una Ubicación
Para poder crear una o más ubicaciones, necesitarás el ID de una categoría. Usa el endpoint anterior para obtener las categorías y seleccionar el ID que corresponde a la categoría deseada. Luego, puedes usar este ID al crear las ubicaciones.

##### 4. Crear Ubicación (s)
Una vez que tengas el ID de la categoría, puedes crear una o varias ubicaciones asociadas con ella utilizando el siguiente endpoint:

**POST /api/v1/locations/**
**Descripción:**
Crea una o varias ubicaciones, asociándolas con una categoría mediante el ID obtenido en el paso anterior. El cuerpo de la solicitud debe incluir los detalles de las ubicaciones, como el nombre, descripción y coordenadas.
##### 5. Explorar Recomendaciones
Para obtener recomendaciones de ubicaciones que aún no han sido revisadas o que no se han revisado en más de 30 días, utiliza el siguiente endpoint:

**GET /api/v1/recommendations/explore**
**Descripción:**
Este endpoint devuelve una lista de ubicaciones que necesitan revisión, es decir, que no han sido revisadas o que su última revisión fue hace más de 30 días. Esto puede ser útil para encontrar ubicaciones de interés que podrían requerir atención.
##### 6. Buscar Ubicaciones Cercanas
Finalmente, puedes buscar ubicaciones cercanas a una ubicación específica, utilizando las coordenadas de latitud y longitud. Este endpoint también actualizará la fecha de la última visualización (last_view_at), lo que permite rastrear cuándo se visualizó una ubicación por última vez.

**GET /api/v1/locations/nearby**
**Descripción:**
Este endpoint busca ubicaciones cercanas a una posición geográfica dada (latitud y longitud). También actualiza el campo last_view_at para las ubicaciones encontradas, lo que indica la última vez que se visualizó cada ubicación.

### Ejecutar Test
```bash
pytest
```
## Estructura del Proyecto
```bash
challenge-orbidi
├── alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
├── alembic.ini
├── docker
│   └── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── main.py
├── Makefile
├── pytest.ini
├── requirements.txt
├── src
│   ├── api
│   │   ├── dependencies.py
│   │   └── v1
│   │       ├── endpoints
│   │       │   ├── categories.py
│   │       │   ├── locations.py
│   │       │   └── recomendations.py
│   │       └── router.py
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── models
│   │   ├── base.py
│   │   ├── category.py
│   │   ├── location.py
│   │   └── review.py
│   ├── repositories
│   │   ├── base.py
│   │   ├── category.py
│   │   ├── location.py
│   │   └── recomendation.py
│   ├── schemas
│   │   ├── base.py
│   │   ├── category.py
│   │   ├── location.py
│   │   └── recomendation.py
│   └── services
│       ├── base_service.py
│       ├── category.py
│       ├── location.py
│       └── recomendation.py
└── tests
    ├── test_base_service.py
    ├── test_category_service.py
    ├── test_location_service.py
    └── test_recomendation_service.py
```
### Arquitectura
En este proyecto, se ha optado por implementar una arquitectura en capas (Layered Architecture) debido a su simplicidad y efectividad para organizar y gestionar la separación de responsabilidades. La arquitectura en capas divide la aplicación en distintas capas funcionales, cada una encargada de una tarea específica. Esto permite un mantenimiento más fácil, mejora la escalabilidad y facilita la comprensión del sistema a medida que crece.

### Razones para elegir Layered Architecture:
- *Simplicidad y claridad*: La arquitectura en capas es fácil de entender y seguir. Al dividir la aplicación en capas como la de presentación, lógica de negocio y acceso a datos, se facilita la colaboración entre equipos y se mejora la legibilidad del código.

- *Separación de responsabilidades*: Cada capa tiene una responsabilidad claramente definida. Esto no solo ayuda a organizar el código, sino que también mejora la capacidad de realizar pruebas unitarias y facilita el mantenimiento del sistema a lo largo del tiempo.

- *Escalabilidad y flexibilidad*: La arquitectura en capas permite agregar nuevas funcionalidades o modificar las existentes sin afectar otras partes del sistema, lo que es clave a medida que el proyecto crece.

### Alternativas Viables
Si bien la arquitectura en capas ha sido la elección principal, también se considera la posibilidad de implementar Clean Architecture o Arquitectura Hexagonal.

Clean Architecture: Este enfoque organiza el código en círculos concéntricos, con el núcleo de la aplicación (la lógica de negocio) siendo independiente de las interfaces externas, lo que permite una gran flexibilidad para realizar cambios sin afectar la lógica de negocio.

Arquitectura Hexagonal: También conocida como "Ports and Adapters", permite una comunicación flexible entre el núcleo de la aplicación y sus interfaces externas (como bases de datos o servicios externos), mejorando el desacoplamiento y facilitando las pruebas.

### Descripción
- `alembic/`: Contiene scripts y configuraciones para las migraciones de la base de datos.
- `docker/`: Archivos relacionados con la configuración de Docker.
- `src/api/`: Define los endpoints de la API y las dependencias.
- `src/core/`: Configuración de la aplicación, la base de datos y manejo de excepciones.
- `src/models/`: Define los modelos de datos.
- `src/repositories/`: Contiene el acceso a los datos y las operaciones CRUD.
- `src/schemas/`: Define los esquemas de datos para validación y serialización.
- `src/services/`: Contiene la lógica de negocio y las operaciones de servicio.
- `tests/`: Contiene pruebas unitarias e integración para los diferentes servicios.

---
## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.


