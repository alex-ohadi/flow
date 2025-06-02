FROM python:3.9-slim

# Create working directory
WORKDIR /app

# Copy only the requirements first for better caching
COPY a_producer/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies (e.g., for psycopg2 or other Postgres libraries)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Now copy the rest of your code
COPY a_producer/ ./a_producer

# Set the working directory to where the producer script is
WORKDIR /app/a_producer/build

# Expose the Pulsar port (only needed if the container needs incoming Pulsar traffic)
EXPOSE 6650

# Set the command to run the producer
CMD ["python", "producer_push.py"]
