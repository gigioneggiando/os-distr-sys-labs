from flask import Flask
import requests
from datetime import date, timedelta

app = Flask(__name__)

@app.route("/weather/<postcode>")
def weather(postcode):
    try:
        # 1️⃣ Get city, latitude, longitude from Zippopotam
        url_zip = f"https://api.zippopotam.us/DK/{postcode}"
        resp_zip = requests.get(url_zip)
        resp_zip.raise_for_status()
        data_zip = resp_zip.json()
        place = data_zip["places"][0]
        city = place["place name"]
        lat = place["latitude"]
        lon = place["longitude"]

        # 2️⃣ Get forecast data from Open-Meteo
        url_meteo = (
            "https://api.open-meteo.com/v1/forecast"
            f"?timezone=auto&daily=temperature_2m_max,temperature_2m_min"
            f"&latitude={lat}&longitude={lon}"
        )
        resp_meteo = requests.get(url_meteo)
        resp_meteo.raise_for_status()
        data_meteo = resp_meteo.json()

        # 3️⃣ Get tomorrow's temperatures
        days = data_meteo["daily"]["time"]
        tmin = data_meteo["daily"]["temperature_2m_min"]
        tmax = data_meteo["daily"]["temperature_2m_max"]
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        if tomorrow in days:
            idx = days.index(tomorrow)
        else:
            idx = 1  # fallback

        temp_min = tmin[idx]
        temp_max = tmax[idx]

        # 4️⃣ Response
        return f"The temperature in {city} will be between {temp_min} and {temp_max} tomorrow"

    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
