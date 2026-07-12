#!/usr/bin/env bash
#
# Exercise 09 – start ten Docker containers from a single script
#
# What the script does:
#   1️⃣ Creates a Docker network (named “exercise_net” by default)
#   2️⃣ Launches ten containers on that network
#   3️⃣ Gives each container a deterministic name:
#        bash_container_1 … bash_container_10
#
# Prerequisites
#   • Docker Engine must be installed and running
#   • Your user must be able to run Docker commands
#       – either run the script with sudo or add your user to the “docker”
#         group (e.g. sudo usermod -aG docker $USER && newgrp docker)
#   • An image to run – the script uses the lightweight “alpine” image,
#     but you can swap it for any image you prefer.
#
# Save this file as, for example, start_ten_containers.sh and make it executable:
#   chmod +x start_ten_containers.sh
# Then run it:
#   ./start_ten_containers.sh
#

set -euo pipefail   # exit on error, treat unset vars as errors, fail pipelines

# ----------------------------------------------------------------------
# Configuration (feel free to tweak)
# ----------------------------------------------------------------------
NETWORK_NAME="exercise_net"          # name of the Docker network
IMAGE="alpine"                       # base image for the containers
CONTAINER_PREFIX="bash_container_"   # prefix for container names
COUNT=10                             # how many containers to launch

# ----------------------------------------------------------------------
# 1️⃣ Create the Docker network (ignore error if it already exists)
# ----------------------------------------------------------------------
if docker network ls --filter "name=^${NETWORK_NAME}$" --format "{{.Name}}" | grep -q "^${NETWORK_NAME}$"; then
    echo "Network '${NETWORK_NAME}' already exists – skipping creation."
else
    echo "Creating network '${NETWORK_NAME}' ..."
    docker network create "${NETWORK_NAME}"
fi

# ----------------------------------------------------------------------
# 2️⃣ Start the containers in a loop
# ----------------------------------------------------------------------
for i in $(seq 1 ${COUNT}); do
    CONTAINER_NAME="${CONTAINER_PREFIX}${i}"
    
    # Check if a container with this name already exists (avoid duplicate errors)
    if docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "Container '${CONTAINER_NAME}' already exists – skipping."
        continue
    fi
    
    echo "Starting container '${CONTAINER_NAME}' ..."
    
    # The container runs indefinitely (sleep infinity) so it stays alive.
    # You can replace the command with anything you need.
    docker run -d \
        --name "${CONTAINER_NAME}" \
        --network "${NETWORK_NAME}" \
        "${IMAGE}" \
        sh -c "while true; do sleep 3600; done"
done

echo "All done! ${COUNT} containers are now running on network '${NETWORK_NAME}'."
