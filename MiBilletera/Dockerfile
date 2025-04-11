# Usa una imagen base liviana
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt

COPY . .

EXPOSE 5000

# Definir el comando de ejecución
CMD ["python", "/code/app/main.py"]