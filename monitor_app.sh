#!/bin/bash

# Flask App Health Monitor
# This script continuously monitors the Flask app and restarts it if it crashes
# Run this in the background: nohup /path/to/monitor_app.sh &

STARTUP_SCRIPT="/Users/zopdev/ research/start_app.sh"
LOG_FILE="/tmp/flask_monitor.log"
CHECK_INTERVAL=30  # Check every 30 seconds

echo "[$(date)] Flask app monitor started" >> "$LOG_FILE"

while true; do
    # Check if app is running on port 8080
    if ! lsof -i :8080 > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  Flask app is not running! Restarting..." >> "$LOG_FILE"
        "$STARTUP_SCRIPT" restart >> "$LOG_FILE" 2>&1
    else
        # App is running, log status quietly
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Flask app is healthy" >> "$LOG_FILE"
    fi

    # Wait before next check
    sleep $CHECK_INTERVAL
done
