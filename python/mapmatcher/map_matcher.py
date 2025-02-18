import os
import json
import pulsar
import time
import sys
import pymongo
from datetime import datetime
from pymongo import MongoClient

# Add the build directory to sys.path
sys.path.append(os.path.abspath('build'))

# Attempt to import the module
try:
    import hmm_map_matcher
    print("Module 'hmm_map_matcher' successfully imported!")
except ImportError as e:
    print("Error importing 'hmm_map_matcher':", e)

# Max retries and delay settings
MAX_RETRIES = 20
DELAY_SECONDS = 20

def connect_to_pulsar():
    """ Attempt to connect to Pulsar with retries. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}: Connecting to Pulsar broker...")
            pulsar_client = pulsar.Client('pulsar://pulsar-broker:6650', operation_timeout_seconds=30, connection_timeout_ms=10000, io_threads=4, message_listener_threads=4)
            print("✅ Successfully connected to Pulsar client!")
            return pulsar_client
        except Exception as e:
            print(f"❌ Connection attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    print("🚨 Failed to connect after multiple attempts. Exiting.")
    exit(1)

def create_producer(client):
    """ Attempt to create a producer with retries and logging. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}: Creating producer...")
            producer = client.create_producer('persistent://public/default/gps-traces')
            print("✅ Successfully created producer!")
            return producer
        except Exception as e:
            print(f"❌ Producer creation attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    print("🚨 Failed to create producer after multiple attempts. Exiting.")
    exit(1)

def create_consumer(client):
    """ Attempt to create a consumer with retries and logging. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}: Creating consumer...")
            consumer = client.subscribe(
                'persistent://public/default/gps-traces',
                subscription_name='gps-trace-subscription'
            )
            print("✅ Successfully created consumer!")
            return consumer
        except Exception as e:
            print(f"❌ Consumer creation attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    print("🚨 Failed to create consumer after multiple attempts. Exiting.")
    exit(1)

def connect_to_mongodb():
    """ Establish connection to MongoDB with retries. """
    mongo_user = os.getenv("data_username")
    mongo_password = os.getenv("data_password")
    mongo_host = "mongodb-map-matcher"
    mongo_port = "27017"

    if not mongo_user or not mongo_password:
        print("🚨 MongoDB username or password is missing from environment variables. Exiting.")
        exit(1)

    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/data"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}: Connecting to MongoDB...")
            client = MongoClient(mongo_uri)
            db = client["data"]
            collection = db["datas"]
            print("✅ Successfully connected to MongoDB!")
            return collection
        except Exception as e:
            print(f"❌ MongoDB connection attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)

    print("🚨 Failed to connect to MongoDB after multiple attempts. Exiting.")
    exit(1)

# Initialize connections
pulsar_client = connect_to_pulsar()
producer = create_producer(pulsar_client)
consumer = create_consumer(pulsar_client)
mongo_collection = connect_to_mongodb()

# Function to send a GPS trace to Pulsar
def send_gps_trace(gps_trace_data):
    message = json.dumps(gps_trace_data)
    producer.send(message.encode('utf-8'))
    print(f" Sent GPS trace: {gps_trace_data}")

# Function to consume GPS trace data from Pulsar
def consume_gps_trace():
    msg = consumer.receive()
    gps_trace_data = json.loads(msg.data().decode('utf-8'))
    consumer.acknowledge(msg)
    return gps_trace_data

# Load the edges data from JSON (road network)
with open('edges2.json', 'r') as edges_file:
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
matcher = hmm_map_matcher.HMMMapMatcher(edges)

# Load the events data from JSON (GPS traces)
with open('events2.json', 'r') as events_file:
    events_data = json.load(events_file)

# List to collect all matched segments
all_matched_segments = []

# Send the GPS traces to Pulsar
for event in events_data:
    gps_trace_data = {
        "lat": event["lat"],
        "lon": event["lon"],
        "timestamp": event["timestamp"]
    }
    send_gps_trace(gps_trace_data)

# Consume and map-match the GPS traces
for _ in range(len(events_data)):
    received_trace = consume_gps_trace()
    print(f"📥 Received GPS trace: {received_trace}")

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


# Final data to push into MongoDB
document_to_insert = {
    "timestamp_utc": datetime.utcnow().isoformat(),
    "matched_data": all_matched_segments
}


def insert_large_document_in_parts(mongo_collection, document):
    # Split the document into smaller parts (for example, by list of matched segments)
    part_size = 1000  # Adjust size to fit within BSON limit
    segments = document.get('matched_data', [])
    
    # Insert each part separately
    for i in range(0, len(segments), part_size):
        part = {**document, 'matched_data': segments[i:i + part_size]}  # Split the segments
        try:
            mongo_collection.insert_one(part)
            print(f"✅ Successfully inserted part {i//part_size + 1}.")
        except Exception as e:
            print(f"🚨 Failed to insert part {i//part_size + 1}: {e}")

# Call the function
insert_large_document_in_parts(mongo_collection, document_to_insert)

# Close Pulsar client connection
pulsar_client.close()
