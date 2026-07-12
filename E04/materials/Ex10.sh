#!/usr/bin/env bash
#
# Exercise 10 – clean up containers created in Exercise 09
# -------------------------------------------------------
# Expected resources:
#   * Containers: bash_container_1 … bash_container_10
#   * Network:   exercise_net
#
# Save as cleanup_exercise.sh, make executable, and run:
#   chmod +x cleanup_exercise.sh
#   ./cleanup_exercise.sh          # or sudo ./cleanup_exercise.sh
#

set -euo pipefail   # abort on any unexpected error

# -------------------------- CONFIGURATION --------------------------
NETWORK_NAME="exercise_net"
CONTAINER_PREFIX="bash_container_"
# ------------------------------------------------------------------

# Helper: pretty header
header() { echo -e "\n=== $* ==="; }

# ----------------------------------------------------------------------
# 1️⃣ Find all containers that contain the prefix (running OR stopped)
# ----------------------------------------------------------------------
header "Looking for containers with prefix '${CONTAINER_PREFIX}'"
container_ids=$(docker ps -aq -f "name=${CONTAINER_PREFIX}") || true

if [[ -z "$container_ids" ]]; then
    echo "No containers matching prefix '${CONTAINER_PREFIX}' were found."
else
    echo "Found the following containers:"
    docker ps -a -f "name=${CONTAINER_PREFIX}" \
        --format "  {{.ID}}\t{{.Names}}"

    # ------------------------------------------------------------------
    # 2️⃣ Stop any that are still running (immediate timeout)
    # ------------------------------------------------------------------
    header "Stopping any running containers"
    running_ids=$(docker ps -q -f "name=${CONTAINER_PREFIX}") || true
    if [[ -n "$running_ids" ]]; then
        docker stop -t 0 $running_ids
    else
        echo "No running containers to stop."
    fi

    # ------------------------------------------------------------------
    # 3️⃣ Force‑remove all containers (detaches them from the network)
    # ------------------------------------------------------------------
    header "Force‑removing containers"
    docker rm -f $container_ids
    echo "All matching containers have been removed."
fi

# ----------------------------------------------------------------------
# 4️⃣ Remove the network (if it still exists)
# ----------------------------------------------------------------------
header "Checking for network '${NETWORK_NAME}'"
if docker network ls --filter "name=^${NETWORK_NAME}$" --format "{{.Name}}" \
        | grep -q "^${NETWORK_NAME}$"; then
    header "Removing network '${NETWORK_NAME}'"
    docker network rm "${NETWORK_NAME}"
    echo "Network '${NETWORK_NAME}' removed."
else
    echo "Network '${NETWORK_NAME}' does not exist – nothing to delete."
fi

header "Cleanup completed successfully"
exit 0
