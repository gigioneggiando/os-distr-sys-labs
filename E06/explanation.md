# Theoretical background

## Lab idea
The application receives a postal code, fetches city and coordinates from an external API, and then queries a second service to obtain tomorrow's weather.

## Call chain
1. Flask exposes `GET /weather/<postcode>`.
2. The route calls Zippopotam to convert the postal code into city, latitude, and longitude.
3. The route calls Open-Meteo to obtain the daily forecast.
4. The final response combines the data into a readable sentence.

## Concepts to highlight
- `requests.get()` is synchronous: each call blocks until the response arrives.
- An error from an external dependency is caught and turned into a `500` response.
- The container does not change the application logic: it only makes it portable and repeatable.

## Teaching points
- The code clearly shows the difference between application logic and integration with external services.
- The app works only if the container has Internet access.
- The route path is static, but the returned data changes based on the API.
