import os
import json
import pulsar
import time
import sys
from datetime import datetime
import psycopg2
from psycopg2 import sql
import logging

# Set up logging to stdout (Docker captures stdout)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')

# Add the build directory to sys.path
sys.path.append(os.path.abspath('build'))

# Attempt to import the module
try:
    import hmm_map_matcher
    logging.info("Module 'hmm_map_matcher' successfully imported!")
except ImportError as e:
    logging.error("Error importing 'hmm_map_matcher':", e)

# Max retries and delay settings
MAX_RETRIES = 20
DELAY_SECONDS = 20

def connect_to_pulsar():
    """ Attempt to connect to Pulsar with retries. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Connecting to Pulsar broker...")
            pulsar_client = pulsar.Client('pulsar://pulsar-broker:6650', operation_timeout_seconds=30, connection_timeout_ms=10000, io_threads=4, message_listener_threads=4)
            logging.info("✅ Successfully connected to Pulsar client!")
            return pulsar_client
        except Exception as e:
            logging.error(f"❌ Connection attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    logging.error("🚨 Failed to connect after multiple attempts. Exiting.")
    exit(1)

def create_producer(client):
    """ Attempt to create a producer with retries and logging. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Creating producer...")
            producer = client.create_producer('persistent://public/default/gps-traces')
            logging.info("✅ Successfully created producer!")
            return producer
        except Exception as e:
            logging.error(f"❌ Producer creation attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    logging.error("🚨 Failed to create producer after multiple attempts. Exiting.")
    exit(1)

def create_consumer(client):
    """ Attempt to create a consumer with retries and logging. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Creating consumer...")
            consumer = client.subscribe(
                'persistent://public/default/gps-traces',
                subscription_name='gps-trace-subscription'
            )
            logging.info("✅ Successfully created consumer!")
            return consumer
        except Exception as e:
            logging.error(f"❌ Consumer creation attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    logging.error("🚨 Failed to create consumer after multiple attempts. Exiting.")
    exit(1)

def connect_to_postgresql():
    """ Establish connection to PostgreSQL with retries. """
    postgres_user = os.getenv("PGUSER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_host = os.getenv("POSTGRES_HOST") 
    postgres_db = os.getenv("POSTGRES_DB", "data")

    if not postgres_user or not postgres_password:
        logging.error("🚨 PostgreSQL username or password is missing from environment variables. Exiting.")
        exit(1)

    connection_string = f"dbname={postgres_db} user={postgres_user} password={postgres_password} host={postgres_host}"
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Connecting to PostgreSQL...")
            connection = psycopg2.connect(connection_string)
            cursor = connection.cursor()
            logging.info("✅ Successfully connected to PostgreSQL!")
            return connection, cursor
        except Exception as e:
            logging.error(f"❌ PostgreSQL connection attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    logging.error("🚨 Failed to connect to PostgreSQL after multiple attempts. Exiting.")
    exit(1)

# Initialize connections
logging.info("Connecting to Pulsar and PostgreSQL...")
pulsar_client = connect_to_pulsar()
producer = create_producer(pulsar_client)
consumer = create_consumer(pulsar_client)
postgres_connection, postgres_cursor = connect_to_postgresql()

# Function to send a GPS trace to Pulsar
def send_gps_trace(gps_trace_data):
    message = json.dumps(gps_trace_data)
    producer.send(message.encode('utf-8'))
    logging.info(f" Sent GPS trace: {gps_trace_data}")

# Function to consume GPS trace data from Pulsar
def consume_gps_trace():
    msg = consumer.receive()
    gps_trace_data = json.loads(msg.data().decode('utf-8'))
    consumer.acknowledge(msg)
    return gps_trace_data

# Load the edges data from JSON (road network)
logging.info("Loading edges.json...")
with open('edges.json', 'r') as edges_file:
    edges_data = json.load(edges_file)

# Convert edges to RoadSegment objects
edges = []
for edge in edges_data:
    road_segment = hmm_map_matcher.RoadSegment()
    road_segment.id = edge["id"]
    coordinates = []
    for coord in edge["gps"]["coordinates"]:
        gps_point = hmm_map_matcher.GPSPoint()
        gps_point.latitude = coord[1]
        gps_point.longitude = coord[0]
        coordinates.append(gps_point)
    road_segment.coordinates = coordinates
    edges.append(road_segment)

# Initialize the matcher
logging.info("Initialize the map matcher..")
matcher = hmm_map_matcher.HMMMapMatcher(edges)

# Load the events data from JSON (GPS traces)
logging.info("Loading events.json...")
with open('events.json', 'r') as events_file:
    events_data = json.load(events_file)

# List to collect all matched segments
all_matched_segments = []

# Send the GPS traces to Pulsar
logging.info("Creating gps trace data...")
for event in events_data:
    gps_trace_data = {
        "lat": event["lat"],
        "lon": event["lon"],
        "timestamp": event["timestamp"]
    }
    send_gps_trace(gps_trace_data)

# Consume and map-match the GPS traces
logging.info("Consuming and map-matching the GPS traces...")
for _ in range(len(events_data)):
    received_trace = consume_gps_trace()
    logging.info(f"📥 Received GPS trace: {received_trace}")

    # Convert received trace to GPSPoint object
    gps_point = hmm_map_matcher.GPSPoint()
    gps_point.latitude = received_trace["lat"]
    gps_point.longitude = received_trace["lon"]

    # Match the trace to the road network
    matched_segments = matcher.matchTraceToRoads([gps_point])

    # Add to all_matched_segments list
    all_matched_segments.append({
        "gps_trace": received_trace,
        "matched_segments": matched_segments
    })

# Final data to push into PostgreSQL
logging.info("Creating document to insert into PostgreSQL")
document_to_insert = {
    "timestamp_utc": datetime.utcnow().isoformat(),
    "matched_data": all_matched_segments
}

def insert_large_document_in_parts(cursor, connection, document):
    """ Insert large document into PostgreSQL in parts. """
    part_size = 1000 
    segments = document.get('matched_data', [])
    
    insert_query = sql.SQL("INSERT INTO datas (timestamp_utc, matched_data) VALUES (%s, %s)")

    logging.info(f"Total segments: {len(segments)}. Part size: {part_size}. The loop will run {len(segments) // part_size + (1 if len(segments) % part_size != 0 else 0)} times.")

    for i in range(0, len(segments), part_size):
        part = {**document, 'matched_data': segments[i:i + part_size]}  # Split the segments
        
        try:
            cursor.execute(insert_query, (part['timestamp_utc'], json.dumps(part['matched_data'])))
            connection.commit()  # Commit after each part
            logging.info(f"✅ Successfully inserted part {i//part_size + 1}.")
        except Exception as e:
            connection.rollback()  # Rollback if there's an error
            logging.error(f"🚨 Failed to insert part {i//part_size + 1}: {e}")

# Call the function
logging.info("Logging into Postgres")
insert_large_document_in_parts(postgres_cursor, postgres_connection, document_to_insert)

# Close Pulsar client connection
pulsar_client.close()
