FROM python:3.9-slim

WORKDIR /app

COPY python/requirements.txt .

# For postgres
RUN apt-get update && apt-get install -y libpq-dev gcc

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libpython3-dev \
    pybind11-dev \
    nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/python/mapmatcher
RUN cmake -S . -B build && make -C build
RUN mv build/libhmm_map_matcher.so build/hmm_map_matcher.so

EXPOSE 6650

CMD ["python", "map_matcher.py"]
# CMD ["tail", "-f", "/dev/null"]
