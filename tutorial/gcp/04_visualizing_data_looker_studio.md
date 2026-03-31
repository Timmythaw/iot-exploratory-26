# IoT Exploratory 2026: Visualizing Data with Looker Studio

**Goal:** Your simulated edge data is now safely stored in Google BigQuery. However, raw database rows are hard to read. In this lab, we will connect Looker Studio to BigQuery and build a professional, auto-updating dashboard to visualize your temperature, humidity, and light data over time.

---

## Prerequisites
1. You have successfully deployed your Cloud Function.
2. Your `simulate_sensors.py` script is running (or has run recently) so there is data in your BigQuery `sensor_data` table.

---

## Step 1: Connect to Looker Studio using a Custom Query
Because we saved our sensor data inside a JSON string column called `payload`, we need to extract those values into standard columns (like numbers and dates) so Looker Studio can graph them. We will do this using a Custom SQL Query.

1. Open a new browser tab and go to [lookerstudio.google.com](https://lookerstudio.google.com/).
2. Log in with the same Google Account you used for Google Cloud.
3. Click the large **Blank Report** button (or **Create** > **Report**).
4. *If prompted, fill out your country/company details and accept the terms.*
5. In the "Add data to report" menu, click the **BigQuery** connector. 
6. Click **Authorize** to allow Looker Studio to view your Google Cloud projects.
7. Instead of choosing "My Projects", click **Custom Query** on the left menu.
8. Select your project (`iot-exploratory-2026`) from the project list.
9. Paste the following SQL query into the box. 
   
   **🚨 CRITICAL:** You must change `group1_workshop_demo` to match your actual dataset name!

```sql
SELECT 
  TIMESTAMP(timestamp) as event_time,
  device_id,
  CAST(JSON_VALUE(payload, '$.temperature') AS FLOAT64) as temperature,
  CAST(JSON_VALUE(payload, '$.humidity') AS FLOAT64) as humidity,
  CAST(JSON_VALUE(payload, '$.light_level') AS INT64) as light_level
FROM `iot-exploratory-2026.group1_workshop_demo.sensor_data`
```

10. Click the **Add** button in the bottom right corner, then click **Add to Report**.

*What did we just do? We told BigQuery to read the JSON string, pluck out the temperature, humidity, and light level, turn them into standard numbers (`FLOAT64` and `INT64`), and convert our text timestamp into a real time-object (`TIMESTAMP`).*

## Step 2: Build a Time Series Line Chart (Temp & Humidity)
Let's plot how our temperature and humidity change over time. Looker Studio will usually drop a random table on the screen when you first connect—you can click on it and press `Delete` on your keyboard to clear the canvas.

1. In the top toolbar, click **Add a chart** > **Time series chart** (the first line chart option).

2. Click anywhere on the blank canvas to place it. Resize it to make it wide.

3. Look at the Setup panel on the right side of the screen:

    - **Date Range Dimension**: Ensure this is set to `event_time`.

    - **Dimension**: Ensure this is also set to `event_time`.

    - **Metric**: This dictates what is being graphed. Remove whatever is there (like `Record Count`) by clicking the `X`.

    - Click **Add metric** and select `temperature`.

    - Click **Add metric** again and select `humidity`.

4. *Optional Styling*: Click the Style tab at the top of the right panel. Under "Series #2" (your humidity), check the box for **Right Y-Axis**. This puts temperature on the left scale and humidity on the right scale so they don't squash each other!

## Step 3: Add a Gauge for Light Level
Line charts are great for history, but sometimes we just want to see the latest value at a glance.

1. Click **Add a chart** > **Gauge** (scroll down to the bottom of the list).

2. Place it on your dashboard next to your line chart.

3. In the right **Setup** panel:

    - Metric: Change this to `light_level`.

4. By default, the gauge might try to "Sum" all your light levels together. Click the little pencil icon next to `light_level` in the Metric section, and change the **Aggregation** from `Sum` to `Average` or `Max`.

5. In the **Style** tab, you can set the Max value of the axis to `1000` (since our simulated light tops out around 800).

## Step 4: Add Dashboard Controls
Let's make the dashboard interactive so users can filter the data.

1. In the top toolbar, click **Add a control** > **Date range control**.

2. Place the box in the top right corner of your report.

3. Click it, and set the default date range to **Today** or **Auto**. Now, anyone viewing the dashboard can filter for specific days!

4. Click **Add a control** again > **Drop-down list**.

5. Place it near the top. In the setup panel, ensure the Control field is set to `device_id`.

    - *If you had multiple simulated sensors running, you could use this dropdown to filter the charts to look at only one specific device!*

## Step 5: Make it Auto-Refresh and Share
By default, Looker Studio caches data for about 12 hours to save database costs. For an IoT workshop, we want it faster.

1. At the very top menu, click **File** > **Report Settings**.

2. At the bottom of the right panel, find "Data Freshness".

3. Click your custom query data source and change the freshness from 12 hours to **15 minutes**.

4. To view your finished product, click the blue **View** button in the top right corner.

5. You can share this dashboard just like a Google Doc by clicking the **Share** button and adding your teammates' emails.

---

You have built a complete, end-to-end cloud data pipeline. Your edge devices push data to Pub/Sub, a serverless Cloud Function processes it, BigQuery stores it, and Looker Studio brings it to life.

You are now ready to move on to the next lab: **Sending Commands from Looker Studio to the Edge.** 

Proceed to [Part 5: Sending Commands from Looker Studio to the Edge](./05_sending_cmd_from_looker_studio_to_edge.md) to continue!**