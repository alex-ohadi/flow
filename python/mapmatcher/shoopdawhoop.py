import sys
import os
import json
import pulsar  # Import Pulsar client
import time

# Add the build directory to sys.path
sys.path.append(os.path.abspath('build'))

# Attempt to import the module
try:
    import hmm_map_matcher
    print("Module 'hmm_map_matcher' successfully imported!")
except ImportError as e:
    print("Error importing 'hmm_map_matcher':", e)

# Max retries and delay settings for connecting to pulsar
MAX_RETRIES = 10
DELAY_SECONDS = 15

def connect_to_pulsar():
    """ Attempt to connect to Pulsar with retries. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}: Connecting to Pulsar broker...")
            pulsar_client = pulsar.Client('pulsar://pulsar-broker:6650')
            print("Successfully connected to Pulsar client!")
            return pulsar_client
        except Exception as e:
            print(f"Connection attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    print("🚨 Failed to connect after multiple attempts. Exiting.")
    exit(1)

def create_producer(client):
    """ Attempt to create a producer with retries and logging. """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempt {attempt}: Creating producer...")
            producer = client.create_producer('persistent://public/default/gps-traces')
            print("Successfully created producer!")
            return producer
        except Exception as e:
            print(f"Producer creation attempt {attempt} failed: {e}")
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
            print("Successfully created consumer!")
            return consumer
        except Exception as e:
            print(f"Consumer creation attempt {attempt} failed: {e}")
            time.sleep(DELAY_SECONDS)
    
    print("Failed to create consumer after multiple attempts. Exiting.")
    exit(1)

# Main execution
pulsar_client = connect_to_pulsar()
producer = create_producer(pulsar_client)
consumer = create_consumer(pulsar_client)

# Function to send a GPS trace to Pulsar
def send_gps_trace(gps_trace_data):
    message = json.dumps(gps_trace_data)  # Convert GPS trace to JSON
    producer.send(message.encode('utf-8'))  # Send message to Pulsar topic
    print(f"Sent GPS trace: {gps_trace_data}")

# Function to consume GPS trace data from Pulsar
def consume_gps_trace():
    msg = consumer.receive()
    gps_trace_data = json.loads(msg.data().decode('utf-8'))  # Decode message from Pulsar
    consumer.acknowledge(msg)  # Acknowledge message receipt
    return gps_trace_data

# Load the edges data from JSON (this contains the road network)
with open('edges.json', 'r') as edges_file:
    edges_data = json.load(edges_file)

# Convert the dictionary to RoadSegment objects
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

# Initialize the matcher with the road network
matcher = hmm_map_matcher.HMMMapMatcher(edges)

# Load the events data from JSON (this contains the GPS traces)
with open('events.json', 'r') as events_file:
    events_data = json.load(events_file)

# List to collect all matched segments
all_matched_segments = []

# Send the GPS traces to Pulsar
for event in events_data:
    gps_trace_data = {
        "lat": event["lat"],
        "lon": event["lon"],
        "timestamp": event["timestamp"]  # Include any other necessary fields
    }
    send_gps_trace(gps_trace_data)

# Consume and map-match the GPS traces
for _ in range(len(events_data)):  # Assuming we're consuming as many events as we sent
    received_trace = consume_gps_trace()
    print(f"Received GPS trace: {received_trace}")

    # Convert received GPS trace to GPSPoint object for map matching
    gps_point = hmm_map_matcher.GPSPoint()
    gps_point.latitude = received_trace["lat"]
    gps_point.longitude = received_trace["lon"]

    # Now pass the list of GPSPoint objects to matchTraceToRoads
    matched_segments = matcher.matchTraceToRoads([gps_point])

    # Print matched road segments
    print("Matched Road Segments:")
    print(matched_segments)

    # Add the matched segments to the list of all matched segments
    all_matched_segments.append(matched_segments)

# Pretty print the entire matched segments data and save it to 'output.json'
with open('output.json', 'w') as output_file:
    json.dump(all_matched_segments, output_file, indent=4)
    print("All data has been saved to 'output.json'.")

# Close Pulsar client connection
pulsar_client.close()
