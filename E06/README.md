# Lab 06 Guide: Network Introduction & APIs

This folder contains a self-contained version of the lab about using external APIs and building a small containerized Flask application.

## Contents
- [explanation.md](explanation.md) with the service flow.
- [guide.md](guide.md) with the steps to explain to students.
- [materials/](materials) with the app, Dockerfile, and dependencies.
- [solutions/](solutions) with the question PDF and answer sheet.

## Lab goal
Understand how an HTTP request in Flask can orchestrate multiple calls to external services and turn a simple route into a complete microservice.

## Quick start
1. Open a terminal in this folder.
2. Build the image:
   ```bash
   docker build -t lab06-network -f materials/Dockerfile materials
   ```
3. Start the container:
   ```bash
   docker run -p 5000:5000 lab06-network
   ```
4. Test the route:
   ```bash
   curl http://localhost:5000/weather/5000
   ```
   Returns a sentence such as `The temperature in Odense C will be between
   19.3 and 23.9 tomorrow` (exact numbers vary by day).

Verified: the image builds and the route above was tested against the live
Zippopotam and Open-Meteo APIs, returning a valid combined response.

## About the question PDF
`solutions/questions.pdf` (`E06_Network & APIs.pdf`) has 7 exercises.
`materials/` only implements the last one (Exercise 07, the combined
Geocoding + Weather API); Exercises 01, 02, 05, and 06 need an external
account, a live packet capture, or a bare `curl` call and are answered as
procedure/expected-output in `solutions/answers.md` instead.
