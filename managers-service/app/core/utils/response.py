from flask import jsonify


def success_response(data=None, message='Operación exitosa', status_code=200):
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(message='Error en la operación', status_code=400, errors=None):
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code
