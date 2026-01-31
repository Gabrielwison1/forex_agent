#!/bin/bash

# Ensure DB is initialized before anything starts
echo "Initializing Cloud Database..."
PYTHONPATH=. python -c "from src.database.models import init_db; init_db()"

# Start the Trading Agent in the background with AUTOMATIC RESTART
echo "Starting Trading Agent with auto-restart protection..."
sleep 5

# Infinite restart loop for the agent
(
  while true; do
    echo "[$(date)] Agent starting..."
    PYTHONPATH=. python src/main.py
    AGENT_EXIT_CODE=$?
    echo "[$(date)] Agent exited with code $AGENT_EXIT_CODE. Restarting in 10 seconds..."
    sleep 10
  done
) &

# Start the Streamlit Dashboard in the foreground
echo "Starting Dashboard..."
PYTHONPATH=. streamlit run src/dashboard/app.py --server.port $PORT --server.address 0.0.0.0
