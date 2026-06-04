FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir "ramose @ git+https://github.com/opencitations/ramose.git@v2.1.0"

WORKDIR /app
COPY oc.hf /app/oc.hf

EXPOSE 8081
CMD ["python", "-m", "ramose", "-s", "/app/oc.hf", "-w", "0.0.0.0:8081", "--no-cache"]
