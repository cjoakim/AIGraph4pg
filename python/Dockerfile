FROM    python:3.11-alpine
WORKDIR /app
RUN     mkdir -p /app/tmp
RUN     apk add gcc python3-dev
RUN     apk add gcc musl-dev linux-headers python3-dev
COPY    . .
RUN     pip install --upgrade pip
RUN     pip install -r requirements-docker.txt
RUN     pip list
EXPOSE  8001
CMD     ["uvicorn", "webapp:app", "--host", "0.0.0.0", "--port", "8000"]

# This file contains the instructions for building the Docker image.
# Chris Joakim, 3Cloud
#
# Developer Notes:
# docker build -t cjoakim/aigraph4pg .
# docker image ls
# docker ps
# docker stop -t 2 008038664a58
#
# DockerHub:
# docker push cjoakim/aigraph4pg:latest
