FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /vantage-publisher

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY config.json config.json
COPY parameters.json parameters.json
COPY airlink.py airlink.py
#COPY vantage-publisher.py vantage-publisher.py

COPY vantage-publisher-threading.py vantage-publisher.py
CMD ["python", "-u", "vantage-publisher.py"]
