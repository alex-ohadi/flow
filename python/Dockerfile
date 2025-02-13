# Step 1: Use a Python base image
FROM python:3.9-slim

# Step 2: Set the working directory to /app
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY python/requirements.txt .

# Step 4: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the entire project directory into the container
COPY . .

# Step 6: Install system dependencies (for building C++ code)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libpython3-dev \
    pybind11-dev \
    nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Step 7: Build the C++ code
WORKDIR /app/python/mapmatcher
RUN cmake -S . -B build && make -C build
RUN mv build/libhmm_map_matcher.so build/hmm_map_matcher.so

# Expose the port for communication
EXPOSE 6650

# Step 9: Set the command to run the Python script (adjust as necessary)
CMD ["python", "shoopdawhoop.py"]
# CMD ["tail", "-f", "/dev/null"]
