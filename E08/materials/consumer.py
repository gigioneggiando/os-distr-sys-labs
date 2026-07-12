import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "users-raw-data",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",          # also reads events that are already present
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

print("Listening on 'users-raw-data' (Ctrl+C to exit)...")
for msg in consumer:
    data = msg.value
    # Still works even if the event shape changes
    username = data.get("username") or data.get("raw", {}).get("login", {}).get("username")
    email = data.get("email") or data.get("raw", {}).get("email")
    print(f"Username: {username}, Email: {email}")
