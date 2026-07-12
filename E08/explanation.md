# Theoretical background

## Lab idea
The producer generates user events in JSON format and sends them to a Kafka topic. The consumer listens on the same topic and prints the received messages.

## Core concepts

### Producer
It is the component that creates and publishes events.

### Consumer
It is the component that reads and processes already published events.

### Topic
It is the logical channel where messages are written and read.

### Offset
Each message has a position in the topic; `auto_offset_reset="earliest"` makes the consumer start from the beginning if it has no previous state.

### Serialization
Python objects are converted to JSON before sending and converted back into dictionaries when read.

## What to observe
- The producer uses an external API to generate realistic data.
- The consumer is independent from the producer: it can stay running and read new or already existing events.
- The Kafka broker separates producers from consumers and absorbs traffic spikes.
