# Guide for the student assistant

## Recommended path
1. First explain the producer/consumer model in the abstract.
2. Open [materials/producer.py](materials/producer.py) and point out how it builds the event.
3. Open [materials/consumer.py](materials/consumer.py) and explain why it reads from `earliest`.
4. Show [materials/docker-compose.yml](materials/docker-compose.yml) and connect the broker to port `9092`.

## Points to emphasize
- The producer does not talk directly to the consumer.
- Kafka is a persistent buffer, not just a volatile queue.
- The JSON format makes the events easy to read during the lab.

## Useful questions
- Why do we use a topic instead of sending data directly to the consumer?
- What happens if the consumer starts after the producer?
- Why is it useful to have an intermediate broker?
