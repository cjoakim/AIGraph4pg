#!/bin/bash

# This script executes the complete set of unit tests
# for the app_common package, with code coverage.
# Note: The Graph microservice should be running on localhost
# when these tests are executed.
# Chris Joakim, 3Cloud

mkdir -p tmp

rm tmp/*.*

source bin/activate

echo 'reformatting source code with black ...'
black .

echo 'executing unit tests with code coverage ...'
pytest -v --cov=src/ --cov-report html tests/
