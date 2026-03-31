# IoT Exploratory 2026: Simulating Edge Device Data to Pub/Sub

**Goal:** Before we wire up the physical ESP32 microcontrollers, we need to test our Google Cloud pipeline (Pub/Sub -> Cloud Functions -> BigQuery/Firestore). In this lab, you will run a Python script that acts exactly like your Raspberry Pi edge gateway, generating fake temperature, humidity, and light data, and publishing it to the cloud.

---

## Prerequisites
1. You must have completed the **Google Cloud Setup Guide** and authenticated your terminal.
2. You must have your Service Account JSON key downloaded (e.g., `group1-key.json`).
3. You must have Python installed on your system (Raspberry Pi OS or WSL Ubuntu).

---

## Step 1: Install the Google Cloud Pub/Sub Library
Your Python script needs the official Google Cloud library to communicate securely with Pub/Sub. Open your terminal and run:

```bash
pip install google-cloud-pubsub
```

(Note: If you are on a Raspberry Pi and get a "managed environment" error, use pip install google-cloud-pubsub --break-system-packages or run it inside a Python virtual environment).

## Step 2: Create the Simulation Script
Create a new file named simulate_sensors.py. You can use an IDE like VS Code, or a terminal editor like `nano`:

```bash
nano simulate_sensors.py
```

Paste the following Python code into the file.

🚨 CRITICAL: You must update the `GROUP_NAME` and `PROJECT_ID` variables at the top of the script to match your specific group!

```python
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
```

Save and exit the file (If using nano, press Ctrl+O, Enter, then Ctrl+X).

## Step 3: Run the Simulation
Ensure your JSON key file (e.g., `group1-key.json`) is sitting in the exact same folder as your `simulate_sensors.py` script.

Run the script from your terminal:

```bash
python3 simulate_sensors.py
```

## Expected Output:
If your authentication and variables are correct, you should see your terminal start printing successful publish messages every 5 seconds:

```plaintext
Starting simulation for group1...
Target Topic: projects/iot-exploratory-2026/topics/group1-telemetry-up
Press Ctrl+C to stop.
--------------------------------------------------
Published! [Cloud ID: 123456789012345] | Temp: 24.5°C | Hum: 60.2%
Published! [Cloud ID: 123456789012346] | Temp: 25.1°C | Hum: 58.7%
```
---

You are now streaming live, simulated telemetry data directly into Google Cloud Pub/Sub. You can leave this script running in the background while you check BigQuery and Firestore to verify the data is arriving safely.

You are now ready to move on to the next lab: **Processing Pub/Sub Data with Cloud Functions.** 

Proceed to [Part 3: Processing Pub/Sub Data with Cloud Functions](./03_processing_pubsub_data_cloud_function.md) to continue!**