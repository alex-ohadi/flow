import os
import json
import pulsar
import time
import logging
import sys

# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')

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

# Initialize Pulsar client and producer
pulsar_client = connect_to_pulsar()
producer = create_producer(pulsar_client)

# Load GPS traces from events.json
logging.info("Loading events.json...")
with open('events.json', 'r') as events_file:
    events_data = json.load(events_file)

# Send the GPS traces to Pulsar
logging.info("Sending GPS traces to Pulsar...")
for event in events_data:
    gps_trace_data = {
        "lat": event["lat"],
        "lon": event["lon"],
        "timestamp": event["timestamp"]
    }
    message = json.dumps(gps_trace_data)
    producer.send(message.encode('utf-8'))
    logging.info(f"📤 Sent GPS trace: {gps_trace_data}")

logging.info("✅ All GPS traces sent!")

# Close the Pulsar connection
pulsar_client.close()
