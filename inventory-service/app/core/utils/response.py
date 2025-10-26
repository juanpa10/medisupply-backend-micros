"""
Utilidades para respuestas HTTP estandarizadas
"""
from flask import jsonify


def success_response(data=None, message='Operación exitosa', status_code=200):
    """
    Genera una respuesta de éxito estandarizada
    
    Args:
        data: Datos a retornar
        message: Mensaje de éxito
        status_code: Código HTTP
        
    Returns:
        Tupla (response, status_code)
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(message='Error en la operación', status_code=400, errors=None):
    """
    Genera una respuesta de error estandarizada
    
    Args:
        message: Mensaje de error
        status_code: Código HTTP
        errors: Detalles adicionales del error
        
    Returns:
        Tupla (response, status_code)
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def paginated_response(items, page, per_page, total, message='Datos obtenidos exitosamente'):
    """
    Genera una respuesta paginada estandarizada
    
    Args:
        items: Lista de items
        page: Página actual
        per_page: Items por página
        total: Total de items
        message: Mensaje de éxito
        
    Returns:
        Tupla (response, status_code)
    """
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        'success': True,
        'message': message,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), 200
