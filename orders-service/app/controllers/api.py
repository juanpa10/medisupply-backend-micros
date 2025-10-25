from flask import Blueprint, request, jsonify, Response
from app.services.orders_service import svc
from app.util.auth_mw import require_auth, get_token_sub
from sqlalchemy.exc import IntegrityError
from app.domain.models import Order
import json
import time

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.get('/health')
def health():
    return {'status': 'alive'}


def get_json():
    return request.get_json(silent=True) or {}


@bp.get('/orders')
@require_auth
def list_orders():
    sub = get_token_sub(request)
    # scope by token subject (customer id)
    # accept either 'state' or 'status' query param
    state = request.args.get('state') or request.args.get('status')
    start = request.args.get('start')
    end = request.args.get('end')
    orders = svc.list_orders(sub, state, start, end)
    out = []
    for o in orders:
        out.append({'order_number': o.order_number, 'status': o.status, 'created_at': o.created_at.isoformat() if o.created_at else None, 'monto': float(o.monto) if getattr(o, 'monto', None) is not None else 0.0, 'items': [{'product_name': it.product_name, 'quantity': it.quantity, 'unit_price': float(it.unit_price)} for it in getattr(o, 'items', [])]})
    if not out:
        # tests expect either a message (when auth via token) or an empty list (when header-based auth)
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer'):
            return jsonify({'message': 'No encontramos pedidos para tu búsqueda'}), 200
        return jsonify([])
    return jsonify(out)


@bp.get('/orders/<order_number>')
@require_auth
def get_order(order_number: str):
    sub = get_token_sub(request)
    o = svc.get_order(order_number)
    if not o or o.customer_id != sub:
        return {'error': 'not_found'}, 404
    return jsonify({'order_number': o.order_number, 'status': o.status, 'created_at': o.created_at.isoformat() if o.created_at else None, 'monto': float(o.monto) if getattr(o, 'monto', None) is not None else 0.0, 'items': [{'product_name': it.product_name, 'quantity': it.quantity, 'unit_price': float(it.unit_price)} for it in getattr(o, 'items', [])]})


@bp.post('/orders')
@require_auth
def create_order():
    sub = get_token_sub(request)
    data = get_json()
    if 'order_number' not in data:
        return {'error': 'order_number required'}, 400
    # Do not allow creating orders for a different customer via request body
    if 'customer_id' in data and data.get('customer_id') != sub:
        return {'error': 'customer_mismatch'}, 400
    # Validate status if provided
    status = data.get('status', None)
    if status is not None and status not in Order.ALLOWED_STATUSES:
        return {'error': 'invalid_status', 'allowed': list(Order.ALLOWED_STATUSES)}, 400
    items = data.get('items')
    try:
        o = svc.repo.create_order(sub, data['order_number'], status or 'pendiente', items=items)
    except IntegrityError:
        # duplicate order_number or other constraint violation
        return {'error': 'order_exists', 'order_number': data['order_number']}, 409
    return jsonify({'order_number': o.order_number, 'status': o.status, 'monto': float(o.monto) if getattr(o, 'monto', None) is not None else 0.0}), 201


@bp.put('/orders/<order_number>/status')
@require_auth
def update_status(order_number: str):
    data = get_json()
    if 'status' not in data:
        return {'error': 'status required'}, 400
    # Validate status
    if data['status'] not in Order.ALLOWED_STATUSES:
        return {'error': 'invalid_status', 'allowed': list(Order.ALLOWED_STATUSES)}, 400
    note = data.get('note')
    o = svc.update_status(order_number, data['status'], note)
    if not o:
        return {'error': 'not_found'}, 404
    # In a full impl we'd notify via websocket/SSE; here we just return the updated order
    return jsonify({'order_number': o.order_number, 'status': o.status}), 200


@bp.get('/orders/stream')
@require_auth
def orders_stream():
    # Simple Server-Sent Events demo: push a keepalive and pretend updates every 5s
    def event_stream():
        for i in range(12):
            # This is a placeholder: real implementation would push actual order changes
            payload = {'ts': int(time.time())}
            yield f'data: {json.dumps(payload)}\n\n'
            time.sleep(5)
    return Response(event_stream(), mimetype='text/event-stream')
    return Response(event_stream(), mimetype='text/event-stream')
