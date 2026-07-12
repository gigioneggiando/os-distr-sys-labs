# Lab 08 Solutions: Streaming

`solutions/questions.pdf` (`E08_Streaming.pdf`) walks through four tasks: run a
Kafka broker in Docker, test it with the CLI tools, write a Python producer,
and write a Python consumer. Answers follow that order and were verified by
actually running the lab (see the "Verification" note at the end of each
section).

## Task 1: Run Kafka in a Docker container

**PDF instructions.** Start a broker with the official image:
```bash
docker run -d -p 9092:9092 --name broker apache/kafka:latest
```

**This lab's implementation.** `materials/docker-compose.yml` starts a
**Redpanda** broker instead of the official Apache Kafka image. Redpanda
implements the Kafka wire protocol, so it is a drop-in replacement for
`kafka-python`/the Kafka CLI tools, while being much lighter to start than a
full Kafka + ZooKeeper (or KRaft) stack. Start it with:
```bash
docker compose -f materials/docker-compose.yml up -d
```
Both approaches expose port `9092` and behave identically from the
producer/consumer's point of view.

**Verification.** Ran `docker compose -f materials/docker-compose.yml up -d`;
the container logs show `Successfully started Redpanda!` and `Started Kafka
API server listening at ... port: 9092`.

## Task 2: Test your setup

**PDF instructions.**
1. `docker exec --workdir /opt/kafka/bin/ -it broker sh` — shell into the
   broker container.
2. `./kafka-topics.sh --bootstrap-server localhost:9092 --create --topic test-topic`
   — create a topic.
3. `./kafka-console-producer.sh --bootstrap-server localhost:9092 --topic
   test-topic` — type `hello`, Enter, `world`, Enter, then Ctrl+C.
4. `./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic
   test-topic --from-beginning` — should print back `hello` and `world`.

**Answer.** These CLI paths (`/opt/kafka/bin/...`) are specific to the official
`apache/kafka` image used in the PDF. With the Redpanda image used in
`materials/docker-compose.yml`, the equivalent is Redpanda's own CLI, `rpk`,
already on the container's `PATH`:
```bash
docker exec -it materials-kafka-1 rpk topic create test-topic
docker exec -it materials-kafka-1 rpk topic produce test-topic   # type hello, Enter, world, Enter, Ctrl+D
docker exec -it materials-kafka-1 rpk topic consume test-topic
```
The observable result is the same either way: whatever lines you produce are
read back by the consumer, demonstrating that Kafka (or a Kafka-protocol
broker like Redpanda) persists messages in a topic rather than requiring the
producer and consumer to be connected to each other directly.

## Task 3: Create a Kafka Producer

**PDF instructions.** In Python, using `kafka-python`, fetch a fictional user
from the Random User API and send 10 user events as JSON to a topic called
`users-raw-data`.

**Answer — implemented in `materials/producer.py`.**
1. Connects with `KafkaProducer(bootstrap_servers="localhost:9092",
   value_serializer=lambda v: json.dumps(v).encode("utf-8"))`.
2. Loops 10 times; each iteration calls `GET https://randomuser.me/api/` and
   takes the first entry from `"results"`.
3. Builds an event `{"username": ..., "email": ..., "raw": <full user object>}`
   from `user["login"]["username"]` and `user["email"]`, keeping the full raw
   record too.
4. Sends the event with `producer.send(TOPIC, event)` (`TOPIC =
   "users-raw-data"`) and flushes immediately, printing progress like
   `[3/10] Sent: crazywolf607 - supriya.andrade@example.com`.

Run with `pip install -r materials/requirements.txt` then `python
materials/producer.py` (the topic is auto-created by the broker; no manual
`kafka-topics.sh --create` step is required with this setup).

**Verification.** Ran `python producer.py` against the Redpanda broker from
Task 1 and it sent and printed all 10 events successfully, e.g.:
```
[1/10] Sent: angryfish822 - oceane.lacroix@example.com
...
[10/10] Sent: silversnake459 - remedios.garcia@example.com
Done.
```

## Task 4: Create a Kafka Consumer

**PDF instructions.** Read events from the topic and print
`Username: USERNAME, Email: EMAIL` for each one, extracted from the JSON
content of each event.

**Answer — implemented in `materials/consumer.py`.**
1. Connects with `KafkaConsumer("users-raw-data",
   bootstrap_servers="localhost:9092", auto_offset_reset="earliest",
   enable_auto_commit=True, value_deserializer=lambda m:
   json.loads(m.decode("utf-8")))` — `earliest` means it also reads events
   already sitting in the topic, not just new ones.
2. Iterates over the consumer (`for msg in consumer:` blocks forever, waiting
   for new events).
3. Reads `username`/`email` from the top-level event, falling back to the
   nested `raw.login.username` / `raw.email` fields if the top-level keys are
   ever missing.
4. Prints `Username: {username}, Email: {email}` for each event, matching the
   PDF's required output format exactly.

Run with `python materials/consumer.py` (Ctrl+C to stop).

**Verification.** Ran `python -u consumer.py` right after the producer run
above (with `auto_offset_reset="earliest"` it also picked up the events sent
before it started); it printed all 10 events correctly, e.g.:
```
Listening on 'users-raw-data' (Ctrl+C to exit)...
Username: angryfish822, Email: oceane.lacroix@example.com
...
Username: silversnake459, Email: remedios.garcia@example.com
```
This confirms the producer → broker → consumer chain works end to end with
the materials in this lab.
