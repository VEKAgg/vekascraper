FROM python:3.12-alpine

WORKDIR /app

COPY shared/ /app/shared/
COPY services/message_worker/ /app/services/message_worker/

RUN pip install --no-cache-dir -e /app/shared/ -e /app/services/message_worker/

ENV PYTHONPATH=/app/services/message_worker/src:/app/shared/src
USER 65534

CMD ["python", "-m", "message_worker"]
