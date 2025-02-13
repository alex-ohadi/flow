import sys
import os
import json
import pulsar  # Import Pulsar client

# Add the build directory to sys.path
sys.path.append(os.path.abspath('build'))

# Attempt to import the module
try:
    import hmm_map_matcher
    print("Module 'hmm_map_matcher' successfully imported!")
except ImportError as e:
    print("Error importing 'hmm_map_matcher':", e)

# Pulsar client setup (connection to Pulsar broker)
pulsar_client = pulsar.Client('pulsar://pulsar-broker:6650')

# Create a Pulsar producer to send GPS trace data
producer = pulsar_client.create_producer('persistent://public/default/gps-traces')

# Create a Pulsar consumer to read GPS trace data
consumer = pulsar_client.subscribe('persistent://public/default/gps-traces', 
                                   subscription_name='gps-trace-subscription')

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
