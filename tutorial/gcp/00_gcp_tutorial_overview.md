# IoT Exploratory 2026: End-to-End Cloud IoT Workshop

Welcome to the IoT Exploratory 2026! In this workshop, you are going to build an enterprise-grade, bi-directional Internet of Things (IoT) pipeline. 

Instead of just blinking an LED on a local network, you will connect edge devices (Raspberry Pi and ESP32s) to a highly scalable Google Cloud architecture. You will stream real-time sensor telemetry up to the cloud, store it, visualize it on a professional dashboard, and send commands back down to the physical world.

## Workshop Roadmap
We have divided this hands-on workshop into **6 core modules**:

### 📍 Part 1: Setup GCP and Join the Project
You will not need to set up your own billing account. Instead, you will authenticate your terminal and join the organizer's central Google Cloud Project (`iot-exploratory-2026`). You will use the Google Cloud CLI to provision your group's cloud infrastructure, including Pub/Sub topics, BigQuery datasets, a Firestore database, and secure Service Account keys.

### 📍 Part 2: Simulate Telemetry Data
Before we wire up the physical microcontrollers, we will test the cloud "funnel." You will run a Python script on your machine that acts as a Raspberry Pi edge gateway. This script will generate simulated temperature, humidity, and light data, packaging it into JSON payloads and pushing it to your Pub/Sub uplink topic.

### 📍 Part 3: Processing Pub/Sub with Cloud Functions
Data sitting in Pub/Sub doesn't do us much good on its own. You will write and deploy a serverless Python script (a Cloud Function) that automatically wakes up whenever new sensor data arrives. This function will unpack the data and route it to two places: BigQuery (for historical storage) and Firestore (for real-time web state).

### 📍 Part 4: Visualizing Data with Looker Studio
Raw database rows are hard to read. You will connect Google's Business Intelligence tool, Looker Studio, directly to your BigQuery database. You will learn an industry trick (Custom SQL) to unpack your JSON payloads on the fly, and build a beautiful, auto-updating dashboard with time-series charts and gauges.

### 📍 Part 5: Send Commands from Looker Studio to the Edge
Dashboards shouldn't just be read-only! You will deploy a second, HTTP-triggered Cloud Function to act as a Webhook API. You will then embed interactive buttons into your Looker Studio dashboard that trigger this webhook, dropping control commands (like "fan_on") into your Pub/Sub downlink topic.

### 📍 Part 6: Simulate Actuator Devices
To complete the loop, you will run a final Python script that "listens" to your Pub/Sub downlink subscription. When you click the buttons on your Looker Studio dashboard, you will watch this script instantly receive the command and simulate an ESP32 turning on a fan or playing a song. 

---

**Ready to start building? Proceed to [Part 1: Google Cloud Environment Setup](./01_setup_gcp.md) to begin!**