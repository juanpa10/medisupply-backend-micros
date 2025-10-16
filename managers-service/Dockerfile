FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=9005
EXPOSE 9005


CMD [ "sh", "-c", "gunicorn -w 2 -b 0.0.0.0:${PORT} \"app:create_app()\"" ]
