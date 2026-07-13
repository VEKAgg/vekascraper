FROM python:3.12-alpine

WORKDIR /app

COPY shared/ /app/shared/
COPY services/controller_bot/ /app/services/controller_bot/

RUN pip install --no-cache-dir -e /app/shared/ -e /app/services/controller_bot/

ENV PYTHONPATH=/app/services/controller_bot/src:/app/shared/src
USER 65534

CMD ["python", "-m", "controller_bot"]
