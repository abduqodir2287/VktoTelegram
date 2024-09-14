FROM python:3.11-slim

WORKDIR /src

COPY docker_requirements.txt .
RUN pip install -r docker_requirements.txt
COPY . .
