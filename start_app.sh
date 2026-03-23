#!/bin/bash

# Flask Reddit Dashboard Startup Script
# This script ensures the Flask app is always running on port 8080

APP_DIR="/Users/zopdev/ research"
VENV_DIR="$APP_DIR/venv"
LOG_FILE="/tmp/flask_reddit_dashboard.log"
PID_FILE="/tmp/flask_reddit_dashboard.pid"

# Function to start the Flask app
start_app() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Flask app..." >> "$LOG_FILE"

    # Kill any existing Flask process on port 8080
    pkill -f "python.*app.py" 2>/dev/null || true
    sleep 1

    # Start the app in background with nohup so it survives terminal close
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    nohup python3 app.py >> "$LOG_FILE" 2>&1 &

    # Save the PID
    echo $! > "$PID_FILE"

    # Wait a moment for startup
    sleep 2

    # Verify it's running
    if lsof -i :8080 > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Flask app started successfully (PID: $(cat $PID_FILE))" >> "$LOG_FILE"
        echo "✅ Flask app is running on http://localhost:8080/feed"
        return 0
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Failed to start Flask app" >> "$LOG_FILE"
        return 1
    fi
}

# Function to stop the Flask app
stop_app() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Stopping Flask app..." >> "$LOG_FILE"
    pkill -f "python.*app.py" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Flask app stopped" >> "$LOG_FILE"
}

# Function to check if Flask app is running
check_app() {
    if lsof -i :8080 > /dev/null 2>&1; then
        echo "✅ Flask app is running on http://localhost:8080/feed"
        lsof -i :8080
        return 0
    else
        echo "❌ Flask app is NOT running on port 8080"
        return 1
    fi
}

# Function to restart the Flask app
restart_app() {
    stop_app
    sleep 1
    start_app
}

# Main logic
case "${1:-start}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        check_app
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the Flask app (default)"
        echo "  stop    - Stop the Flask app"
        echo "  restart - Restart the Flask app"
        echo "  status  - Check if Flask app is running"
        exit 1
        ;;
esac
