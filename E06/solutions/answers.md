# Lab 06 Solutions: Network Introduction & APIs

`solutions/questions.pdf` (`E06_Network & APIs.pdf`) contains seven exercises.
Exercises 1, 2, 5, and 6 require an external account, a packet capture, or a bare
`curl` call and are not reproduced by files in `materials/`; exercises 3, 4, and 7
build on each other into the single Flask app in `materials/app.py` /
`materials/Dockerfile`, which implements the final, combined version (exercise 7).
Answers are given in order below, with the corresponding file noted where one
exists.

## Exercise 01: Facebook Developer

**Task recap.** Create a Facebook Developer app, obtain a User Access Token with
the `user_birthday` permission through the Graph API Explorer, then use `curl -H
"Authorization: Bearer <TOKEN>" <endpoint>` to GET your own birthday from
`https://graph.facebook.com/`.

**Answer.** This step is account-bound (it needs a personal Facebook login and a
personal app/token) and cannot be executed unattended from this repository. The
mechanics are: create the app in the Facebook Developer console → open the Graph
API Explorer → generate a User Access Token with the `user_birthday` scope → call
`curl -H "Authorization: Bearer <TOKEN>" "https://graph.facebook.com/me?fields=birthday"`.
A correct call returns JSON of the shape:
```json
{ "birthday": "01/01/2000", "id": "00000000000000000" }
```
This demonstrates a REST API secured with bearer-token authorization, where the
token identifies both the calling app and the authorizing user.

## Exercise 02: Wireshark

**Task recap.** Capture traffic while visiting a website, filter for
SYN/SYN-ACK/ACK, and answer: what is happening, are there ARP messages, are there
DNS messages.

**Answer.** Also requires an interactive packet capture and cannot be run
headlessly here, but the expected findings are:
- **TCP handshake.** Filtering `tcp.flags.syn==1 and tcp.flags.ack==0`, then
  `tcp.flags.syn==1 and tcp.flags.ack==1`, then `tcp.flags.syn==0 and
  tcp.flags.ack==1` shows the three-way handshake: SYN (client requests a
  connection) → SYN/ACK (server agrees) → ACK (client confirms). After that,
  HTTPS data transfer begins.
- **ARP.** You typically will *not* see ARP packets for an already-visited host,
  because the local ARP cache already holds the MAC address for the default
  gateway; ARP is only needed to resolve an IP to a MAC address the first time,
  and only within the local network (it does not cross routers).
- **DNS.** You may or may not see plain DNS packets. If none appear, the likely
  reasons are that the name was already cached, or the browser is using encrypted
  DNS (DoH/DoT), which does not show up as classic port-53 DNS traffic in
  Wireshark.

## Exercise 03: Hello, Flask!

**Task recap.** Build a Flask server with a `/welcome` route returning
`"Welcome to this excellent page!"`, run it, and check
`http://localhost:5000/welcome`.

**Answer.** The standalone version of this route is superseded by the combined
app built in exercise 7, but the minimal implementation is:
```python
from flask import Flask
app = Flask(__name__)

@app.route('/welcome')
def welcome():
    return 'Welcome to this excellent page!'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
```
Installed with `pip3 install Flask` (or `apt-get install python3-pip` first if
`pip3` is missing), then run with `python3 app.py` and check with `curl
http://localhost:5000/welcome`.

## Exercise 04: Hello, `<NAME>`!

**Task recap.** Extend `/welcome` to take a name parameter, respond with
`"Welcome to this excellent page, <NAME>!"`, containerize it, and access it on
host port 7000.

**Answer.** Route extension: `@app.route('/welcome/<name>')` returning
`f'Welcome to this excellent page, {name}!'`. `materials/Dockerfile` shows the
containerization pattern this exercise asks for (Python base image, install
Flask via `requirements.txt`, copy the server file, run it) — the lab's version
publishes the container's port 5000 to host port 7000 with
`docker run -p 7000:5000 <image>`, then
`curl http://localhost:7000/welcome/James` returns
`Welcome to this excellent page, James!`.

## Exercise 05: Public Geocoding API

**Task recap.** Use `curl` against `https://api.zippopotam.us/DK/<POSTCODE>` to
get city/latitude/longitude for a postcode (e.g. Odense), and inspect the JSON
structure.

**Answer.**
```bash
curl https://api.zippopotam.us/DK/5000
```
returns a JSON object with `"places"`, a list containing an object with keys
such as `"place name"`, `"latitude"`, and `"longitude"` for the given Danish
postcode (5000 = Odense C). `materials/app.py` uses exactly this endpoint and
these fields (`place["place name"]`, `place["latitude"]`, `place["longitude"]`)
in its `/weather/<postcode>` route.

## Exercise 06: Public Weather API

**Task recap.** Use `curl` against the Open-Meteo forecast endpoint with a
latitude/longitude (from exercise 5) to get tomorrow's min/max temperature, and
inspect the JSON structure.

**Answer.**
```bash
curl "https://api.open-meteo.com/v1/forecast?timezone=auto&daily=temperature_2m_max,temperature_2m_min&latitude=55.40&longitude=10.38"
```
returns a JSON object with a `"daily"` block containing parallel arrays
`"time"`, `"temperature_2m_max"`, and `"temperature_2m_min"` indexed by day.
`materials/app.py` reads these same three arrays and picks the index matching
tomorrow's ISO date (falling back to index `1` if the exact date is not found).

## Exercise 07: Public APIs — Combined

**Task recap.** Combine exercises 3–6 into one route, `/weather/<postcode>`,
that looks up the postcode via the Geocoding API, feeds the resulting
coordinates into the Weather API, and returns a sentence with the city and
tomorrow's min/max temperature; containerize and run it on host port 7000.

**Answer — fully implemented in `materials/app.py` and executed as part of this
review (see the lab README for the exact commands):**
1. `GET /weather/<postcode>` calls `https://api.zippopotam.us/DK/<postcode>` and
   extracts `city`, `lat`, `lon` from the first entry in `"places"`.
2. It then calls the Open-Meteo forecast endpoint with those coordinates and
   reads the `"daily"` block.
3. It picks the entry for tomorrow's date (`date.today() + timedelta(days=1)`),
   falling back to index `1` if the date is not present in the response.
4. It returns the plain-text sentence:
   `"The temperature in <CITY> will be between <TEMP_MIN> and <TEMP_MAX> tomorrow"`.
5. Any failure in either HTTP call (`requests.raise_for_status()`, missing keys,
   etc.) is caught by the surrounding `try/except` and turned into an
   `"Error: <message>"` response with HTTP status 500.

Verified end to end: `docker build -t lab06-network -f materials/Dockerfile
materials`, `docker run -p 5000:5000 lab06-network`, then
`curl http://localhost:5000/weather/5000` returned
`The temperature in Odense C will be between 19.3 and 23.9 tomorrow` (temperatures
will vary by day), confirming the full Geocoding → Weather → combined-response
chain works inside the container. Note that the Zippopotam response uses
`"Odense C"` (the actual postal-district name) rather than plain `"Odense"`.
