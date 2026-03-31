# IoT Exploratory 2026: Sending Commands from Looker Studio to the Edge

**Goal:** Dashboards shouldn't just show data; they should let you control your environment! Because Looker Studio is a read-only tool, we are going to build an **HTTP Webhook**. You will deploy a Cloud Function that acts as an API endpoint. Then, you will add a button to your Looker Studio dashboard that pings this endpoint to turn on a fan or play a song on your ESP32's passive buzzer.

---

## Architecture Flow
**Looker Studio Button** -> (HTTP Request) -> **Cloud Function Webhook** -> **Pub/Sub (commands-down)** -> **Raspberry Pi** -> **ESP32 (Actuator)**

---

## Step 1: Write the HTTP Cloud Function
Open your terminal (WSL or Raspberry Pi). Let's create a new folder for this specific webhook function.

```bash
mkdir cloud-function-webhook
cd cloud-function-webhook
```

1. Define Dependencies: 

Create your `requirements.txt` file:

```Bash
nano requirements.txt
```

Paste the following:

```Plaintext
functions-framework==3.*
google-cloud-pubsub==2.*
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

2. Write the Logic (`main.py`)
Create the main Python script:

```Bash
nano main.py
```

Paste this code. 

🚨 CRITICAL: Update the `GROUP_NAME` and `PROJECT_ID`!

```Python
import json
import functions_framework
from google.cloud import pubsub_v1

# ==========================================
# 1. CONFIGURATION
# ==========================================
PROJECT_ID = "iot-exploratory-2026"
GROUP_NAME = "group1"  # <-- Change to your group name

# Initialize Pub/Sub Client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, f"{GROUP_NAME}-commands-down")

# ==========================================
# 2. HTTP WEBHOOK HANDLER
# ==========================================
@functions_framework.http
def send_device_command(request):
    """HTTP Cloud Function to send commands to edge devices."""
    
    # Extract parameters from the URL (e.g., ?device_id=esp32-act-01&action=fan_on)
    request_args = request.args
    device_id = request_args.get('device_id', 'esp32-act-01')
    action = request_args.get('action', 'unknown')

    if action == 'unknown':
        return "Error: No action specified. Use ?action=fan_on or ?action=play_song", 400

    # Build the exact command packet our Raspberry Pi bridge expects
    command_packet = {
        "device_id": device_id,
        "packet_type": "tggs.node.command.v1",
        "payload": {
            "command": action
        }
    }

    try:
        # Publish to the downlink Pub/Sub topic
        data_string = json.dumps(command_packet)
        publisher.publish(topic_path, data=data_string.encode("utf-8"))
        
        # Return a simple success message to the browser
        return f"Success! Command '{action}' dispatched to {device_id}.", 200
    except Exception as e:
        return f"Failed to send command: {e}", 500
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

## Step 2: Deploy the Webhook Function
Now we deploy this to Google Cloud. Notice that the `--trigger` flag is different this time! We are using `--trigger-http` instead of a Pub/Sub topic.

Run this command:

```Bash
gcloud functions deploy group1-send-command \
  --gen2 \
  --runtime=python311 \
  --region=asia-southeast3 \
  --source=. \
  --entry-point=send_device_command \
  --trigger-http \
  --allow-unauthenticated
```
*(Note: --allow-unauthenticated means anyone with the URL can click the button. In a production environment, we would lock this down with IAM tokens!)*

**CRITICAL STEP**: When the deployment finishes, the terminal will print a **Trigger URL** (it will look something like `https://group1-send-command-abc123def-as.a.run.app`). **Copy this URL**!

## Step 3: Add the Control Buttons to Looker Studio
Now, let's wire it up to our dashboard.

1. Open your Looker Studio dashboard and click Edit in the top right.

2. In the top toolbar, click **Add a control** -> **Button**.

3. Place the button on your dashboard.

4. In the right-hand Setup panel:

    - Under **Button Action Type**, select **Navigation**.

    - Under **Button Link URL**, paste the Trigger URL you copied in Step 2, and add `?action=fan_on` to the end of it.
*(Example: `https://group1-send-command-...run.app?action=fan_on`)*

    - Check the box for **Open link in new tab**.

5. Change the button's text to "Turn On Fan" (you can do this by double-clicking the text on the button itself or changing it in the Style tab).

6. **Repeat these steps** to create a second button for your buzzer!

    - Set its URL to: `https://group1-send-command-...run.app?action=play_song`

    - Name it "**Play Song**".

## Step 4: Test the Pipeline!
1. Click the blue View button in the top right of Looker Studio to enter live mode.

2. Click your "**Turn On Fan**" button.

3. A new tab will open briefly, showing your success message ("Success! Command 'fan_on' dispatched...").

4. Behind the scenes, that HTTP request just triggered your Cloud Function, which pushed the message to Pub/Sub, which your Raspberry Pi pulled down, and forwarded via MQTT to your ESP32!

*(Note: Because Looker Studio is fundamentally a reporting tool, opening a new tab is required for security reasons when executing outside links. For a perfectly seamless, single-page experience without opening tabs, developers build custom Web Apps)*

---

You are now ready to move on to the next lab: **Simulating Edge Actuator Device.** 

Proceed to [Part 6: Simulating Edge Actuator Device](./06_simulate_actuator.md) to continue!**
