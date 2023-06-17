FROM python:3.9-alpine3.16

# Install system dependencies
RUN apk add postgresql-client build-base postgresql-dev

# Copy requirements and install dependencies
COPY requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt

# Set up application directory and user
WORKDIR /letsgo
COPY letsgo /letsgo
RUN adduser --disabled-password letsgo-user
USER letsgo-user

EXPOSE 8000
