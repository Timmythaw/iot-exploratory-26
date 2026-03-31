# IoT Exploratory 2026: Processing Pub/Sub Data with Cloud Functions

**Goal:** Now that we have simulated edge data flowing into our Google Cloud Pub/Sub "funnel", we need a way to process it. In this lab, you will write and deploy a **Cloud Function**. This serverless script will automatically wake up every time a new message arrives, unpack the JSON payload, and route it to two places: **BigQuery** (for our historical Looker Studio dashboard) and **Firestore** (for our real-time web app).

---

## Prerequisites
1. You have successfully run the `simulate_sensors.py` script and data is flowing to your Pub/Sub topic.
2. Your BigQuery dataset (`[GROUP_NAME]_workshop_demo`) and tables are created.
3. Your dedicated Firestore database (`[GROUP_NAME]`) is initialized in the `asia-southeast3` region.

---

## Step 1: Prepare Your Workspace
We need a dedicated folder for our Cloud Function code. Open your terminal (WSL or Raspberry Pi) and run the following commands to create and enter a new directory:

```bash
mkdir cloud-function-router
cd cloud-function-router
```

## Step 2: Define Dependencies (`requirements.txt`)
Google Cloud needs to know which Python libraries to install in the serverless container before running your code.

Create a file named `requirements.txt`:

```Bash
nano requirements.txt
```
Paste the following text exactly as shown:

```Plaintext
functions-framework==3.*
google-cloud-bigquery==3.*
google-cloud-firestore==2.*
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

## Step 3: Write the Cloud Function (`main.py`)
This is the core logic of our cloud bridge. Create the main Python file:

```bash
nano main.py
```

Paste the following code.

🚨 **CRITICAL**: You must update the `GROUP_NAME` and `PROJECT_ID` variables at the top of the script!

```python
import base64
import json
import functions_framework
from google.cloud import bigquery
from google.cloud import firestore

# ==========================================
# 1. WORKSHOP CONFIGURATION (UPDATE THESE!)
# ==========================================
PROJECT_ID = "iot-exploratory-2026"
GROUP_NAME = "group1"  # <-- Change to your group name

# Define BigQuery table references
DATASET_ID = f"{GROUP_NAME}_workshop_demo"
SENSOR_TABLE = f"{PROJECT_ID}.{DATASET_ID}.sensor_data"
ACTUATOR_TABLE = f"{PROJECT_ID}.{DATASET_ID}.actuator_data"

# ==========================================
# 2. INITIALIZE CLOUD CLIENTS
# ==========================================
# Declared globally so they stay "warm" between function invocations
bq_client = bigquery.Client(project=PROJECT_ID)
db = firestore.Client(project=PROJECT_ID, database=GROUP_NAME)

# ==========================================
# 3. THE MAIN FUNCTION HANDLER
# ==========================================
@functions_framework.cloud_event
def process_mqtt_message(cloud_event):
    """Cloud Function triggered by a Pub/Sub message."""
    try:
        # A. Decode the Pub/Sub message from base64
        msg_data = cloud_event.data["message"]["data"]
        decoded_msg = base64.b64decode(msg_data).decode("utf-8")
        packet = json.loads(decoded_msg)
        
        print(f"Incoming packet: {packet}")

        # Extract core routing fields
        device_id = packet.get("device_id", "unknown_device")
        packet_type = packet.get("packet_type", "unknown")
        
        # B. ROUTE TO BIGQUERY (Historical Data)
        bq_row = {
            "timestamp": packet.get("timestamp"),
            "device_id": device_id,
            "message_id": packet.get("message_id"),
            "packet_type": packet_type,
            "payload": json.dumps(packet.get("payload", {})) 
        }

        # Route to the correct table
        target_table = SENSOR_TABLE if packet_type == "tggs.node.packet.v1" else ACTUATOR_TABLE

        # Insert into BigQuery
        bq_errors = bq_client.insert_rows_json(target_table, [bq_row])
        if bq_errors:
            print(f"BigQuery Error: {bq_errors}")
        else:
            print(f"Logged to BigQuery table: {target_table}")

        # C. ROUTE TO FIRESTORE (Real-Time State)
        doc_ref = db.collection("devices").document(device_id)
        
        firestore_data = {
            "last_updated": packet.get("timestamp"),
            "packet_type": packet_type,
            "state": packet.get("payload", {})
        }
        
        # merge=True updates existing fields without deleting others
        doc_ref.set(firestore_data, merge=True)
        print(f"Updated Firestore Real-Time State for: {device_id}")

    except Exception as e:
        print(f"System Error processing message: {e}")
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

## Step 4: Deploy to Google Cloud
You now have the code on your local machine. Let's push it to the cloud. We are using **Cloud Functions Gen 2** hosted in the Bangkok (`asia-southeast3`) region for the lowest latency.

Run this deployment command from inside your `cloud-function-router` folder (make sure to replace `group1` with your actual group name):

```bash
gcloud functions deploy group1-pubsub-to-bq \
  --gen2 \
  --runtime=python311 \
  --region=asia-southeast3 \
  --source=. \
  --entry-point=process_mqtt_message \
  --trigger-topic=group1-telemetry-up
```

*Note: This process takes about 2-3 minutes. Google Cloud is packaging your code into a secure container and attaching the Pub/Sub trigger.*

## Step 5: Verify the Pipeline
Once the deployment finishes, start your `simulate_sensors.py` script again (if it isn't already running).

To prove your cloud architecture is fully functional:
1. Go to the Google Cloud Console.
2. Navigate to **BigQuery**.
3. Expand your project (`iot-exploratory-2026`) -> Expand your dataset (`group1_workshop_demo`) -> Click on your **sensor_data table**.
4. Click the Preview tab. You should see your simulated temperature, humidity, and light data actively populating the rows!

## Deep Dive: The Magic Behind the Scenes
When building cloud systems, the automation can often feel like magic. You might be wondering: *How exactly does Pub/Sub know it needs to trigger this specific Cloud Function?*

Pub/Sub doesn't inherently "know" about your code. Instead, Google Cloud built a hidden bridge when you ran the deployment command in Step 4.

The `--trigger-topic` Flag
When you included `--trigger-topic=group1-telemetry-up` in your deployment, you told Google Cloud's engine to do two distinct things:

1. Spin up your Python code inside a secure, serverless container.

2. Create an Eventarc Trigger and a Push Subscription attached to your Pub/Sub topic.

## The Lifecycle of a Message
Because we deployed a Gen 2 Cloud Function, the routing is handled by a Google Cloud service called Eventarc. Here is exactly what happens in milliseconds:

1. **The Arrival**: Your edge device (or the Python simulation script) publishes a JSON message to the Pub/Sub Topic (think of the Topic as a bulletin board).

2. **The Subscription**: Attached to that bulletin board is a Push Subscription. This is a rule that says, *"Whenever a new message gets pinned to this board, take a copy of it and push it to a specific destination."*

3. **The HTTP POST**: The destination is the private internal URL of your newly deployed Cloud Function. Pub/Sub literally takes your message, wraps it in an HTTP POST request, and "calls" your Cloud Function over the internal Google network.

4. **The Wake-Up**: The Cloud Function receives that HTTP request. The `@functions_framework.cloud_event` decorator in your Python code catches it, extracts the payload, and hands it to your script to do the BigQuery and Firestore routing.

5. **The Acknowledgment**: Once your Python code finishes running successfully, the Cloud Function sends an HTTP "200 OK" response back to Pub/Sub. This tells Pub/Sub, *"I processed this successfully; you can now delete it from the queue."*

## The Power of Decoupling
If your Python code has a bug and crashes before it finishes, it won't send that "200 OK" back. Pub/Sub will assume the message wasn't processed and will automatically retry sending the message later. This decoupling is why Pub/Sub is so powerful for IoT—if a database briefly goes offline, Pub/Sub will safely hold onto your sensor data and keep retrying until the system recovers!

---

You are now ready to move on to the next lab: **Visualizing Data with Looker Studio.** 

Proceed to [Part 4: Visualizing Data with Looker Studio](./04_visualizing_data_looker_studio.md) to continue!**