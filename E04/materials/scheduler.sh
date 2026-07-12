#!/bin/bash

# Initialize counters
counter_100ms=0
counter_1s=0
counter_5s=0

# Function to run every 100ms
task_100ms() {
    echo "task 100ms running"
}

# Function to run every 1s
task_1s() {
    echo "task 1s running"
}

# Function to run every 5s
task_5s() {
    echo "task 5s running"
}

# Main loop
while true; do
    # Call task_100ms every loop
    task_100ms
    ((counter_100ms++))

    # Call task_1s every 10 loops (1s)
    if [ $counter_100ms -ge 10 ]; then
        task_1s
        counter_100ms=0
        ((counter_1s++))
    fi

    # Call task_5s every 50 loops (5s)
    if [ $counter_1s -ge 5 ]; then
        task_5s
        counter_1s=0
    fi

    # Sleep for 100ms
    sleep 0.1
done
