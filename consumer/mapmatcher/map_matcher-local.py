import sys
import os
import json

# Add the build directory to sys.path
sys.path.append(os.path.abspath('build'))

# Check if build/ is actually in the sys.path
print(sys.path)

# Attempt to import the module
try:
    import hmm_map_matcher
    print("Module 'hmm_map_matcher' successfully imported!")
except ImportError as e:
    print("Error importing 'hmm_map_matcher':", e)

# Load the edges data from JSON
with open('edges.json', 'r') as edges_file:
    edges_data = json.load(edges_file)

# Convert the dictionary to RoadSegment objects
edges = []
for edge in edges_data:
    # Create RoadSegment objects for each edge
    road_segment = hmm_map_matcher.RoadSegment()
    road_segment.id = edge["id"]
    coordinates = []
    
    # Convert each coordinate to a GPSPoint object
    for coord in edge["gps"]["coordinates"]:
        gps_point = hmm_map_matcher.GPSPoint()
        gps_point.latitude = coord[1]
        gps_point.longitude = coord[0]
        coordinates.append(gps_point)
    
    road_segment.coordinates = coordinates
    edges.append(road_segment)

# Now that edges are correctly populated with RoadSegment objects, initialize the matcher
matcher = hmm_map_matcher.HMMMapMatcher(edges)

# Load events data from JSON
with open('events.json', 'r') as events_file:
    events_data = json.load(events_file)

# Convert events into GPSPoint objects
events = []
for event in events_data:
    gps_point = hmm_map_matcher.GPSPoint()
    gps_point.latitude = event["lat"]
    gps_point.longitude = event["lon"]
    events.append(gps_point)

# Now pass the list of GPSPoint objects to matchTraceToRoads
matched_segments = matcher.matchTraceToRoads(events)

# Print matched road segments
print("Matched Road Segments:")
print(matched_segments)

# Pretty print the matched segments data
pretty_data = json.dumps(matched_segments, indent=4)

# Save the output to a new file 'output.json'
with open('output.json', 'w') as output_file:
    output_file.write(pretty_data)
    print("Data has been saved to 'output.json'.")