#!/usr/bin/env python3
"""
Exercise: List running Docker containers by talking to the Docker daemon
through its Unix domain socket (/var/run/docker.sock).

Requirements (install once):
    pip install requests requests-unixsocket
"""

import json
import sys
from urllib.parse import quote      # <-- URL‑encode the socket path

import requests_unixsocket          # registers the "http+unix://" scheme


def list_running_containers():
    """
    Sends a GET request to the Docker Engine API endpoint that returns only
    the containers that are currently *running* (equivalent to `docker ps`).

    The Docker daemon listens on a Unix‑domain socket, so we have to encode
    the socket path and prepend the special scheme `http+unix://`.
    """
    # ------------------------------------------------------------------
    # 1️⃣ Build the URL
    # ------------------------------------------------------------------
    socket_path = "/var/run/docker.sock"
    # Percent‑encode the path because the URL scheme expects a valid URL.
    encoded_socket = quote(socket_path, safe="")

    # The "?all=0" query tells Docker to return *only* running containers.
    url = f"http+unix://{encoded_socket}/containers/json?all=0"

    # ------------------------------------------------------------------
    # 2️⃣ Perform the request
    # ------------------------------------------------------------------
    try:
        response = requests_unixsocket.get(url, timeout=5)
        response.raise_for_status()          # raise on HTTP error (e.g., 404)
    except Exception as exc:
        # Any problem (socket missing, permission denied, daemon down, …)
        sys.stderr.write(f"Error contacting Docker daemon: {exc}\n")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 3️⃣ Print the result
    # ------------------------------------------------------------------
    containers = response.json()             # Docker returns a JSON array
    print(json.dumps(containers, indent=2))


if __name__ == "__main__":
    list_running_containers()
