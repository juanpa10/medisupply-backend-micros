"""
Utilidad de paginación
"""
from flask import request
from flask import current_app


def get_pagination_params():
    """
    Obtiene los parámetros de paginación desde el request
    
    Returns:
        Tupla (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 
                                current_app.config['DEFAULT_PAGE_SIZE'], 
                                type=int)
    
    # Validar límites
    if page < 1:
        page = 1
    
    max_per_page = current_app.config['MAX_PAGE_SIZE']
    if per_page > max_per_page:
        per_page = max_per_page
    elif per_page < 1:
        per_page = current_app.config['DEFAULT_PAGE_SIZE']
    
    return page, per_page


def paginate_query(query, page=None, per_page=None):
    """
    Pagina una query de SQLAlchemy
    
    Args:
        query: Query de SQLAlchemy
        page: Número de página (opcional)
        per_page: Items por página (opcional)
        
    Returns:
        dict con items, total, page, per_page
    """
    if page is None or per_page is None:
        page, per_page = get_pagination_params()
    
    # Obtener total de items
    total = query.count()
    
    # Aplicar paginación
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page
    }
