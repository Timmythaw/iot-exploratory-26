# IoT Exploratory 2026: Simulating Edge Actuator Device

## Step 1: Create the Pub/Sub Subscription
Before the Python script can listen for commands, we need to attach a subscription to your `commands-down` topic.

Run this command in your terminal (make sure to replace `group1` with your actual group name!):

```Bash
gcloud pubsub subscriptions create group1-commands-sub \
    --topic=group1-commands-down
```

## Step 2: Update Your Looker Studio Buttons
Make sure the URLs on your Looker Studio buttons match our new commands:

* Button 1 (Fan On): https://YOUR_WEBHOOK_URL?action=fan_on

* Button 2 (Fan Off): https://YOUR_WEBHOOK_URL?action=fan_off
 
* Button 3 (Play Song): https://YOUR_WEBHOOK_URL?action=play_song

## Step 3: The Edge Simulation Script (`simulate_actuator.py`)
This script uses the "Pull" method. It sits continuously in a loop, asking Google Cloud: *"Do you have any new commands for me?"* When you click the button in Looker Studio, the message flows down to this script.

Create a new file named `simulate_actuator.py` and paste the following code:

```Python
import os
import json
import time
from google.cloud import pubsub_v1

# ==========================================
# 1. CONFIGURATION (UPDATE THESE!)
# ==========================================
GROUP_NAME = "group1"
PROJECT_ID = "iot-exploratory-2026"
KEY_PATH = f"{GROUP_NAME}-key.json" 
SUBSCRIPTION_ID = f"{GROUP_NAME}-commands-sub"

# ==========================================
# 2. AUTHENTICATION & SETUP
# ==========================================
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# Initialize the Pub/Sub Subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

# ==========================================
# 3. MESSAGE HANDLER (THE BRAIN)
# ==========================================
def process_command(message):
    """This function is triggered every time a new message arrives from the cloud."""
    print(f"\n[PI GATEWAY] Received raw payload from Cloud: {message.data}")
    
    try:
        # Decode the JSON packet
        packet = json.loads(message.data.decode("utf-8"))
        payload = packet.get("payload", {})
        command = payload.get("command", "")
        device_id = packet.get("device_id", "unknown")

        print(f"[PI GATEWAY] Routing command '{command}' to ESP32 ({device_id})...")
        time.sleep(1) # Simulate network travel time to the ESP32
        
        # Simulate the ESP32 reacting to the command
        if command == "fan_on":
            print(">>> [ESP32] 🌀 FAN TURNED ON! Swooshhh...")
        elif command == "fan_off":
            print(">>> [ESP32] 🛑 FAN TURNED OFF! Silence...")
        elif command == "play_song":
            print(">>> [ESP32] 🎵 PLAYING SONG! (Beep boop beep)...")
        else:
            print(f">>> [ESP32] ❓ Unknown command received: {command}")
        
        # CRITICAL: Acknowledge the message so Pub/Sub removes it from the queue
        message.ack()

    except Exception as e:
        print(f"[ERROR] Failed to parse message: {e}")
        # If it fails, negative-acknowledge so Pub/Sub tries sending it again later
        message.nack()

# ==========================================
# 4. START LISTENING
# ==========================================
print(f"Starting Edge Actuator Simulation for {GROUP_NAME}...")
print(f"Listening on Subscription: {subscription_path}")
print("Waiting for Looker Studio button clicks... (Press Ctrl+C to stop)")
print("-" * 60)

# Open the connection to Pub/Sub
streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_command)

try:
    # Keep the main thread alive while the background thread listens
    streaming_pull_future.result()
except KeyboardInterrupt:
    print("\nShutting down edge simulation...")
    streaming_pull_future.cancel()
```

## How to Test It:
1. Ensure your `group1-key.json` is in the same folder as the script.

2. Run the script in your terminal:

    ```Bash
    python3 simulate_actuator.py
    ```

3. Leave the terminal open and visible on your screen.

4. Go to your Looker Studio dashboard.

5. Click your "**Turn On Fan**" button.

6. Watch your terminal! Almost instantly, you will see the Pi gateway receive the payload and the simulated ESP32 turn the fan on with a `🌀 FAN TURNED ON!` message!

---

This conclude the **End-to-End Cloud IoT Workshop**.