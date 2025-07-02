#!/bin/bash

# Start the web app, running within the hypercorn server.
# Entry point is webapp.py, 'app' is the FastAPI object.
# hypercorn enables restarting the app as the Python code changes.
# Chris Joakim, 3Cloud

# ensure that the tmp/ directory exists
mkdir -p tmp/

echo 'activating the venv ...'
source .venv/bin/activate
python --version

# start the web application on port 8080
hypercorn webapp:app --bind 127.0.0.1:8000 --workers 1 --reload
