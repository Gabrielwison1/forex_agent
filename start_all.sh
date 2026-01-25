#!/bin/bash

# Start the Trading Agent in the background
echo "Starting Trading Agent..."
PYTHONPATH=. python src/main.py &

# Start the Streamlit Dashboard in the foreground
echo "Starting Dashboard..."
PYTHONPATH=. streamlit run src/dashboard/app.py --server.port $PORT --server.address 0.0.0.0
