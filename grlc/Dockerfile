FROM python:3.12-slim

RUN pip install --no-cache-dir grlc==1.3.11

WORKDIR /app
COPY config.ini /app/config.ini
COPY queries /app/queries

EXPOSE 8082
CMD ["grlc-server", "--port=8082"]
