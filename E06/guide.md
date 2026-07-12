# Guide for the student assistant

## Recommended path
1. Open [materials/app.py](materials/app.py) and read the route from top to bottom.
2. Explain the input first: the postcode comes from the URL.
3. Then explain the two external services and why they are used in sequence.
4. Point out the `try/except` block and ask what happens if an API does not respond.
5. End with the container and the `docker run -p 5000:5000` command.

## Things to point out to students
- The final result is plain text, not JSON.
- The code uses `requests`, so every step depends on the network.
- `EXPOSE 5000` documents the port, but actual publishing is done by the `-p` flag.

## Useful questions
- Why does the app need two different APIs?
- What happens if the postcode does not exist?
- Why is it useful to containerize this app in Docker?
