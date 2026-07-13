FROM python:3.12-alpine

RUN apk add --no-cache curl

WORKDIR /app

COPY shared/ /app/shared/
COPY services/export_api/ /app/services/export_api/

RUN pip install --no-cache-dir -e /app/shared/ -e /app/services/export_api/

ENV PYTHONPATH=/app/services/export_api/src:/app/shared/src
EXPOSE 8080
USER 65534

CMD ["python", "-m", "export_api"]
