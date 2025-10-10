FROM python:3.11-slim

WORKDIR /srv/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONPATH=/srv/app
ENV FLASK_APP=app.app:app
EXPOSE 9003

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:9003", "app.app:app"]
