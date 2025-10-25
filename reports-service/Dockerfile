FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PORT=9007
EXPOSE 9007
# Use the flask CLI to run on the requested port so the container listens on 9007
CMD ["flask", "run", "--host=0.0.0.0", "--port=9007"]
