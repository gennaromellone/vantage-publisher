FROM python:3.8-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /vantage-publisher

COPY PyVantagePro/ PyVantagePro/
COPY config.json config.json
COPY parameters.json parameters.json
COPY requirements.txt requirements.txt

COPY vantage-publisher.py vantage-publisher.py

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "vantage-publisher.py"]
