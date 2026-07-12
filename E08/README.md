# Lab 08 Guide: Streaming

This folder contains a self-contained version of the lab on the producer/consumer model with Kafka.

## Contents
- [explanation.md](explanation.md) with the data flow and key concepts.
- [guide.md](guide.md) with the steps to use with students.
- [materials/](materials) with the producer, consumer, dependencies, and broker setup.
- [solutions/](solutions) with the question PDF and answer sheet.

## Lab goal
Show how a producer generates events, how a consumer reads them from a topic, and how a Kafka broker acts as a buffer between the two sides.

## Quick start
1. Open a terminal in this folder.
2. Start the broker:
   ```bash
   docker compose -f materials/docker-compose.yml up -d
   ```
3. Install the Python dependencies:
   ```bash
   pip install -r materials/requirements.txt
   ```
4. Start the consumer in one terminal and the producer in another.

   ```bash
   python materials/consumer.py
   python materials/producer.py
   ```

Verified end to end: the broker started, `producer.py` sent 10 fictional users
to the `users-raw-data` topic, and `consumer.py` (with
`auto_offset_reset="earliest"`) printed all 10 as `Username: ..., Email: ...`
lines. See `solutions/answers.md` for the full run.

## About the question PDF
`solutions/questions.pdf` (`E08_Streaming.pdf`) asks for the official
`apache/kafka` image; `materials/docker-compose.yml` uses a Redpanda broker
instead, which speaks the same Kafka protocol and works as a drop-in
replacement for this lab's producer/consumer. See `solutions/answers.md` for
the equivalent CLI commands under each setup.
