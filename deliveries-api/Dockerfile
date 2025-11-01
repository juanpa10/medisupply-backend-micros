FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 9021
ENV FLASK_ENV=production
CMD ["gunicorn","-w","1","-b","0.0.0.0:9021","app.app:app"]
