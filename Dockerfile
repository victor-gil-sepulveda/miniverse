FROM python:2.7-slim-stretch

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

ADD miniverse /app/miniverse

ENV PYTHONPATH "${PYTHONPATH}:/app/miniverse"

CMD python -m miniverse.service.app