#!/bin/bash

# Ensure DB is initialized before anything starts
echo "Initializing Cloud Database..."
PYTHONPATH=. python -c "from src.database.models import init_db; init_db()"

# Start the Trading Agent in the background with a slight delay
echo "Starting Trading Agent..."
sleep 5
PYTHONPATH=. python src/main.py &

# Start the Streamlit Dashboard in the foreground
echo "Starting Dashboard..."
PYTHONPATH=. streamlit run src/dashboard/app.py --server.port $PORT --server.address 0.0.0.0
