FROM python:3.9-slim

WORKDIR /app

COPY python/requirements.txt .

# For postgres

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y \
    libpython3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/python/mapmatcher

EXPOSE 6650

CMD ["python", "producer_push.py"]
