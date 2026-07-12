import json
import time
import requests
from kafka import KafkaProducer

# Connects to the broker exposed on localhost:9092 from the container
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

TOPIC = "users-raw-data"

for i in range(10):
    # Fetch one fake user from the Random User API
    res = requests.get("https://randomuser.me/api/")
    res.raise_for_status()
    user = res.json()["results"][0]

    # Extract a few useful fields and also include the raw JSON
    event = {
        "username": user["login"]["username"],
        "email": user["email"],
        "raw": user,
    }

    # Send the event to the topic
    producer.send(TOPIC, event)
    producer.flush()

    print(f"[{i+1}/10] Sent: {event['username']} - {event['email']}")
    time.sleep(0.2)  # short pause for readability

print("Done.")
