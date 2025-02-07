#!/bin/bash

# Create a minimal python virtual environment for the purpose of running mkdocs.
# THIS SCRIPT IS FOR THE DEVELOPMENT OF AIGRAPH4PG, NOT FOR END-USERS.
# Chris Joakim, Microsoft

# delete previous venv directory
mkdir -p venv 
rm -rf venv 

echo 'creating new venv ...'
python3 -m venv venv

echo 'activating new venv ...'
source venv/bin/activate

echo 'pip install mkdocs ...'
# https://pypi.org/project/mkdocs-material/
pip install mkdocs-material
pip install mkdocs-material[imaging]

pip list
