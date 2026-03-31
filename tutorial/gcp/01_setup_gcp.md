# IoT Exploratory 2026: Google Cloud Environment Setup

**Goal:** Welcome to the Google Cloud IoT Workshop! Before we can send data from our Raspberry Pi and ESP32s, we need to build the cloud infrastructure to catch it. In this lab, you will use the `gcloud` Command Line Interface (CLI) to create your group's Pub/Sub topics, BigQuery tables, Firestore database, and a secure Service Account.

---

## Prerequisites
1. Your workshop organizer has added your Google account to the `iot-exploratory-2026` project.
2. You have a terminal open (WSL on Windows, or the terminal on your Raspberry Pi).
3. The Google Cloud CLI (`gcloud`) is installed on your machine.

---

## Step 1: Authenticate and Connect to the Workshop Project
**🚨 IMPORTANT:** You do *not* need to create a new Google Cloud Project or set up billing! The workshop organizers have already created a central project called `iot-exploratory-2026` and granted your email address access to it.

1. Log in to your Google account from the terminal:
   ```bash
   gcloud auth login
   ```

*This will print a long URL. Hold `Ctrl` and click the link to open your browser, log in with your Google account, and click "Allow".*

2. Link your terminal to the workshop's pre-built project:

    ```bash
    gcloud config set project iot-exploratory-2026
    ```

Set up local variables so we don't have to type our group name over and over.

🚨 **CRITICAL**: Change `group1` to your actual assigned group name!

```bash
export PROJECT_ID="iot-exploratory-2026"
export GROUP_NAME="group1"
```


## Step 2: Create the Pub/Sub "Funnel" (Topics & Subscriptions)
We need two Pub/Sub topics: one for data going UP to the cloud, and one for commands coming DOWN to the edge devices.

1. Create the Uplink Topic (Telemetry):

    ```Bash
    gcloud pubsub topics create $GROUP_NAME-telemetry-up
    ```

2. Create the Downlink Topic (Commands):

    ```Bash
    gcloud pubsub topics create $GROUP_NAME-commands-down
    ```

3. Create a Subscription for the Downlink Topic so your Raspberry Pi can "listen" for commands:

    ```Bash
    gcloud pubsub subscriptions create $GROUP_NAME-commands-sub \
        --topic=$GROUP_NAME-commands-down
    ```

## Step 3: Create the BigQuery Dataset & Tables (Historical Data)
We need a place to store our sensor data history so Looker Studio can graph it. We will create a dataset in the Bangkok region (`asia-southeast3`) for the lowest latency.

1. Create your group's dataset:

    ```Bash
    bq mk --location=asia-southeast3 -d ${PROJECT_ID}:${GROUP_NAME}_workshop_demo
    ```

2. Create the `sensor_data` table:

    ```Bash
    bq mk -t \
    --schema="timestamp:TIMESTAMP,device_id:STRING,message_id:STRING,packet_type:STRING,payload:STRING" \
    ${PROJECT_ID}:${GROUP_NAME}_workshop_demo.sensor_data
    ```

3. Create the actuator_data table:

    ```Bash
    bq mk -t \
    --schema="timestamp:TIMESTAMP,device_id:STRING,message_id:STRING,packet_type:STRING,payload:STRING" \
    ${PROJECT_ID}:${GROUP_NAME}_workshop_demo.actuator_data
    ```

## Step 4: Create the Firestore Database (Real-Time State)
For instant button clicks and real-time dashboard updates, we need a NoSQL database. We will create a dedicated database just for your group.

Run this command to initialize your database in the Bangkok region:

    ```Bash
    gcloud firestore databases create \
        --project=$PROJECT_ID \
        --database=$GROUP_NAME \
        --location=asia-southeast3 \
        --type=firestore-native
    ```

## Step 5: Create a Service Account (Security Keys for the Pi)
Your Raspberry Pi shouldn't use your personal Google login. Instead, we create a "robot account" (Service Account) and give it a secure key file.

1. Create the Service Account:

    ```Bash
    gcloud iam service-accounts create ${GROUP_NAME}-pi-gateway \
        --display-name="Raspberry Pi Gateway for ${GROUP_NAME}"
    ```

2. Grant this account permission to publish to Pub/Sub:

    ```Bash
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${GROUP_NAME}-pi-gateway@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/pubsub.publisher"
    ```

3. Grant this account permission to subscribe (listen) to Pub/Sub:

    ```Bash
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${GROUP_NAME}-pi-gateway@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/pubsub.subscriber"
    ```

4. Download the JSON key file. **Keep this file safe!** Your Python scripts will need it to authenticate.

    ```Bash
    gcloud iam service-accounts keys create ${GROUP_NAME}-key.json \
        --iam-account=${GROUP_NAME}-pi-gateway@${PROJECT_ID}.iam.gserviceaccount.com
    ```

*Verify the file downloaded by running `ls` in your terminal. You should see a file named something like `group1-key.json`.*

--- 

You have successfully provisioned an enterprise-grade cloud architecture. You are now ready to move on to the next lab: **Simulating Edge Device Data to Pub/Sub.**

Proceed to [Part 2: Simulating Edge Device Data to Pub/Sub](./02_simulate_data_to_pubsub.md) to continue!**