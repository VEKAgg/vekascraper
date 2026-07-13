FROM python:3.12-alpine

WORKDIR /app

COPY shared/ /app/shared/
COPY services/member_worker/ /app/services/member_worker/

RUN pip install --no-cache-dir -e /app/shared/ -e /app/services/member_worker/

ENV PYTHONPATH=/app/services/member_worker/src:/app/shared/src
USER 65534

CMD ["python", "-m", "member_worker"]
