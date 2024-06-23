# My FastAPI App

Este proyecto es una aplicación simple construida con FastAPI que imprime "Hola Mundo". La idea es demostrar cómo construir y desplegar una aplicación FastAPI usando buildpacks sin necesidad de un Dockerfile.
1. app.py
Aplicación 

2. requirements.txt
Este archivo especifica las dependencias necesarias para la aplicación.

3. Procfile
Este archivo le dice a buildpacks cómo ejecutar tu aplicación.


Construye el contenedor:
```bash
pack build my-fastapi-app --builder paketobuildpacks/builder:base
```

Ejecuta el contenedor:

```bash
docker run -p 8000:8000 my-fastapi-app
```

Ahora deberías poder navegar a http://localhost:8000 y ver el mensaje "Hello Word from Buildpacks".

