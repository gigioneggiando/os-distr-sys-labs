# Exercise 10 Solution

## Components
- Nginx proxy (HTTPS) on `https://localhost/`
- Backend Flask API in a separate container
- MariaDB in a separate container

## Endpoints
- `POST /person/` saves form data into MariaDB
- `GET /persons/` returns all members as JSON and writes `/tmp/persons.json` in backend

## Run
1. Generate self-signed certs:
   - `mkdir nginx/certs`
   - `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/selfsigned.key -out nginx/certs/selfsigned.crt -subj "/CN=localhost"`
2. Start stack:
   - `docker compose up -d --build`
3. Open:
   - `https://localhost/`

## Notes
- Only Nginx is exposed to host.
- Static files are served at `/`, and other paths are proxied to backend.
