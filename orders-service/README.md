orders-service
=================

Simple microservice to expose customer orders with SSE stream for updates.

Run:

    pip install -r requirements.txt
    python app/app.py

Endpoints:
- GET /api/orders
- POST /api/orders
- POST /api/orders/<order_number>/status
- GET /api/orders/stream (SSE)
orders-service

API endpoints:
- GET /api/orders?customer_id=<>&status=<>&start=<iso>&end=<iso>
- GET /api/orders/<order_number>
- POST /api/orders
- POST /api/orders/<order_number>/status

Port: 9006

Notes:
- For simplicity tests use header X-Customer-Id to scope requests.
- Real deployment should verify JWT token and extract customer id from token's `sub` claim.

Postman collection
------------------

There's a minimal Postman collection in `postman_collection.json` you can import into Postman.

Quick JWT helper (for Postman):

1. Install `pyjwt` or use a Python REPL in the project virtualenv.
2. Generate a token for a customer id (sub):

```python
import jwt, time, os
secret = os.getenv('JWT_SECRET', 'supersecret')
now = int(time.time())
token = jwt.encode({'sub': 'cust-1', 'role': 'viewer', 'iat': now, 'exp': now + 3600}, secret, algorithm='HS256')
print(token)
```

Copy the printed token into the collection variable `{{token}}` or paste it into the Authorization header (Bearer <token>).

Tips:
- Make sure the service is running (via `docker compose up --build -d` from the repository root) and available on port 9006.
- Use `X-Customer-Id` header for simple tests without JWT.
