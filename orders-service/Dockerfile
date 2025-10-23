FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . /app

ENV PYTHONPATH=/app
ENV FLASK_APP=app.app:create_app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=9006

EXPOSE 9006

# Use flask run so the app factory create_app() is honored
CMD ["flask", "run"]
