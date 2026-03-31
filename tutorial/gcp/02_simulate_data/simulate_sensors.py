import os
import json
import time
import uuid
import random
from datetime import datetime, timezone
from google.cloud import pubsub_v1

# ==========================================
# 1. CONFIGURATION (UPDATE THESE!)
# ==========================================
GROUP_NAME = "group1"
PROJECT_ID = "iot-exploratory-2026"

# How many telemetry messages to publish before exiting
MESSAGES_TO_SEND = 100

# The path to the Service Account JSON key you downloaded in Step 5
# Example: "/home/username/group1-key.json" or "C:/Users/Name/group1-key.json"
KEY_PATH = f"{GROUP_NAME}-key.json" 

# ==========================================
# 2. AUTHENTICATION & SETUP
# ==========================================
# Tell the Google Cloud library where to find your credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# Initialize the Pub/Sub Publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, f"{GROUP_NAME}-telemetry-up")

print(f"Starting simulation for {GROUP_NAME}...")
print(f"Target Topic: {topic_path}")
print(f"Will publish {MESSAGES_TO_SEND} messages (Ctrl+C to stop early).")
print("-" * 50)

# ==========================================
# 3. SIMULATION LOOP
# ==========================================
try:
    for _ in range(MESSAGES_TO_SEND):
        # Generate fake sensor values
        simulated_temp = round(random.uniform(22.0, 30.0), 2)
        simulated_hum = round(random.uniform(50.0, 75.0), 2)
        simulated_light = random.randint(300, 800)

        # Build the exact data structure we designed for BigQuery
        message_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": "esp32-sensor-sim-01",
            "message_id": str(uuid.uuid4()),
            "packet_type": "tggs.node.packet.v1",
            "payload": {
                "temperature": simulated_temp,
                "humidity": simulated_hum,
                "light_level": simulated_light
            }
        }

        # Pub/Sub requires the message payload to be a bytestring
        data_string = json.dumps(message_data)
        data_bytes = data_string.encode("utf-8")

        # Publish the message to Pub/Sub
        future = publisher.publish(topic_path, data=data_bytes)
        
        # Wait for the publish to complete and get the Pub/Sub message ID
        published_message_id = future.result()
        
        print(f"Published! [Cloud ID: {published_message_id}] | Temp: {simulated_temp}°C | Hum: {simulated_hum}%")
        
        # Wait 5 seconds before sending the next reading
        time.sleep(5)

    print("-" * 50)
    print("Simulation completed.")

except KeyboardInterrupt:
    print("\nSimulation stopped by user.")
except Exception as e:
    print(f"\nAn error occurred: {e}")