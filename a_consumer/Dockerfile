FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy only the requirements first for better Docker caching
COPY a_consumer/requirements.txt ./a_consumer/requirements.txt

# Install system dependencies for Python packages (e.g., psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install Python dependencies
RUN pip install --no-cache-dir -r a_consumer/requirements.txt

# Install system-level build dependencies for compiling C++ module
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libpython3-dev \
    pybind11-dev \
    nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy entire a_consumer project folder into container
COPY a_consumer/ ./a_consumer

# Build the C++ module
WORKDIR /app/a_consumer/build
RUN cmake -S . -B build && make -C build
RUN mv build/libhmm_map_matcher.so build/hmm_map_matcher.so

# Set port if you're running Pulsar traffic to it (optional for consumer)
EXPOSE 6650

# Run the consumer
CMD ["python", "consumer.py"]
