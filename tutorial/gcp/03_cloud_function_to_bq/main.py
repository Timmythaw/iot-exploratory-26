import base64
import json
import functions_framework
from google.cloud import bigquery
from google.cloud import firestore

# ==========================================
# 1. WORKSHOP CONFIGURATION
# ==========================================
PROJECT_ID = "iot-exploratory-2026"
GROUP_NAME = "group1"  # <-- Students must change this!

# Define BigQuery table references
DATASET_ID = f"{GROUP_NAME}_workshop_demo"
SENSOR_TABLE = f"{PROJECT_ID}.{DATASET_ID}.sensor_data"
ACTUATOR_TABLE = f"{PROJECT_ID}.{DATASET_ID}.actuator_data"

# ==========================================
# 2. INITIALIZE CLOUD CLIENTS
# ==========================================
# We do this outside the main function so they stay "warm" between messages
bq_client = bigquery.Client(project=PROJECT_ID)

# Connect to the specific group's Firestore database we created earlier
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
        
        # B. ROUTE TO BIGQUERY (For Looker Studio History)
        # BigQuery expects the payload column to be a JSON-formatted string
        bq_row = {
            "timestamp": packet.get("timestamp"),
            "device_id": device_id,
            "message_id": packet.get("message_id"),
            "packet_type": packet_type,
            "payload": json.dumps(packet.get("payload", {})) 
        }

        # Decide which table to use based on the packet type
        if packet_type == "tggs.node.packet.v1":
            target_table = SENSOR_TABLE
        else:
            target_table = ACTUATOR_TABLE

        # Insert the row
        bq_errors = bq_client.insert_rows_json(target_table, [bq_row])
        if bq_errors:
            print(f"BigQuery Error: {bq_errors}")
        else:
            print(f"Logged to BigQuery table: {target_table}")


        # C. ROUTE TO FIRESTORE (For Real-Time Dashboard)
        # We create/update a document named after the device_id
        doc_ref = db.collection("devices").document(device_id)
        
        # We store the raw Python dictionary so Firestore can easily read the fields
        firestore_data = {
            "last_updated": packet.get("timestamp"),
            "packet_type": packet_type,
            "state": packet.get("payload", {})
        }
        
        # Using merge=True ensures we update the latest values without deleting other fields
        doc_ref.set(firestore_data, merge=True)
        print(f"Updated Firestore Real-Time State for: {device_id}")

    except Exception as e:
        print(f"System Error processing message: {e}")