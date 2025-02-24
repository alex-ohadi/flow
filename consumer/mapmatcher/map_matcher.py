import os
import json
import pulsar
import time
import sys
from datetime import datetime
import psycopg2
from psycopg2 import sql
import logging

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')

# Add the build directory to sys.path
sys.path.append(os.path.abspath('build'))

# Attempt to import the module
try:
    import hmm_map_matcher
    logging.info("Module 'hmm_map_matcher' successfully imported!")
except ImportError as e:
    logging.error(f"Error importing 'hmm_map_matcher': {e}")

# Max retries and delay settings
MAX_RETRIES = 20
DELAY_SECONDS = 20

def connect_to_pulsar():
    """ Attempt to connect to Pulsar with retries. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Connecting to Pulsar broker...")
            pulsar_client = pulsar.Client('pulsar://pulsar-broker:6650', operation_timeout_seconds=30)
            logging.info("✅ Successfully connected to Pulsar client!")
            return pulsar_client
        except Exception as e:
            logging.error(f"❌ Connection attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    logging.error("🚨 Failed to connect after multiple attempts. Exiting.")
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
consumer = create_consumer(pulsar_client)
postgres_connection, postgres_cursor = connect_to_postgresql()

# Load road network from edges.json
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

# Initialize the map matcher
logging.info("Initializing the map matcher...")
matcher = hmm_map_matcher.HMMMapMatcher(edges)

# Continuous message consumption
logging.info("Starting consumer loop...")
while True:
    logging.info("Receiving messages from consumer..")
    msg = consumer.receive(timeout_millis=5000)
    try:
        received_trace = json.loads(msg.data().decode('utf-8'))
        logging.info(f"📥 Received GPS trace: {received_trace}")

        # Convert received trace to GPSPoint object
        gps_point = hmm_map_matcher.GPSPoint()
        gps_point.latitude = received_trace["lat"]
        gps_point.longitude = received_trace["lon"]

        # Match the trace to the road network
        matched_segments = matcher.matchTraceToRoads([gps_point])

        # Insert into PostgreSQL
        postgres_cursor.execute(
            sql.SQL("INSERT INTO datas (timestamp_utc, matched_data) VALUES (%s, %s)"),
            (datetime.utcnow().isoformat(), json.dumps(matched_segments))
        )
        postgres_connection.commit()

        consumer.acknowledge(msg)
        logging.info("✅ Successfully processed and inserted GPS trace.")
    except Exception as e:
        logging.error(f"❌ Error processing message: {e}")
        consumer.negative_acknowledge(msg)
