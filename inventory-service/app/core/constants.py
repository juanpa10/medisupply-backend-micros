"""
Constantes de la aplicación
"""

# Roles
class Roles:
    ADMIN = 'admin'
    WAREHOUSE_OPERATOR = 'warehouse_operator'
    LOGISTICS_OPERATOR = 'logistics_operator'
    VIEWER = 'viewer'

    ALL_ROLES = [ADMIN, WAREHOUSE_OPERATOR, LOGISTICS_OPERATOR, VIEWER]


# Estados de productos
class ProductStatus:
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DISCONTINUED = 'discontinued'

    ALL_STATUSES = [ACTIVE, INACTIVE, DISCONTINUED]


# Unidades de medida
class MeasurementUnit:
    UNIT = 'unit'
    BOX = 'box'
    PACKAGE = 'package'
    KG = 'kg'
    LITER = 'liter'

    ALL_UNITS = [UNIT, BOX, PACKAGE, KG, LITER]


# Configuración de búsqueda
class SearchConfig:
    MAX_SEARCH_RESULTS = 100
    MIN_SEARCH_LENGTH = 2
    SEARCH_TIMEOUT = 1.0  # segundos
