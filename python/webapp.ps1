# Start the web app, running within the hypercorn server.
# Entry point is webapp.py, 'app' is the FastAPI object.
# hypercorn enables restarting the app as the Python code changes.
# Chris Joakim, Microsoft

# ensure that the tmp/ directory exists
New-Item -ItemType Directory -Force -Path .\tmp | out-null

Write-Host 'activating the venv ...'
.\venv\Scripts\Activate.ps1
python --version

# start the web application on port 8080
hypercorn webapp:app --bind 127.0.0.1:8000 --workers 1 --reload
