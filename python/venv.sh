#!/bin/bash

# Recreate the python virtual environment and reinstall libs on mac/linux.
# Chris Joakim, 3Cloud

# delete previous venv directory
mkdir -p venv 
rm -rf venv 

echo 'displaying python3 location ...'
which python3

echo 'creating new python3 virtual environment in the venv directory ...'
python3 -m venv venv

echo 'activating new venv ...'
source venv/bin/activate

echo 'upgrading pip ...'
python3 -m pip install --upgrade pip 

echo 'install pip-tools ...'
pip install --upgrade pip-tools

echo 'displaying python version'
which python
python3 --version


echo 'pip-compile requirements.in ...'
pip-compile --output-file requirements.txt requirements.in

echo 'pip install requirements.txt ...'
pip install -q -r requirements.txt

echo 'activating virtual environment ...'
source venv/bin/activate

echo ''
echo 'displaying the python version ...'
python3 --version

echo ''
echo 'listing the python libraries installed in this virtual environment ...'
pip list
