"""
Controladores (endpoints) para Suppliers
"""
from flask import request, g, send_file
from marshmallow import ValidationError as MarshmallowValidationError
from app.modules.suppliers.service import SupplierService
from app.modules.suppliers.schemas import (
    SupplierCreateSchema,
    SupplierUpdateSchema,
    SupplierResponseSchema,
    SupplierListSchema
)
from app.core.utils.response import success_response, error_response, paginated_response
from app.core.utils.pagination import paginate_query
from app.core.exceptions import ValidationError
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class SupplierController:
    """Controlador para endpoints de proveedores"""
    
    def __init__(self):
        self.service = SupplierService()
        self.create_schema = SupplierCreateSchema()
        self.update_schema = SupplierUpdateSchema()
        self.response_schema = SupplierResponseSchema()
        self.list_schema = SupplierListSchema()
    
    def create(self):
        """
        POST /api/v1/suppliers
        Crea un nuevo proveedor
        """
        try:
            # Validar datos del formulario
            form_data = request.form.to_dict()
            validated_data = self.create_schema.load(form_data)
            
            # Validar archivo
            if 'certificado' not in request.files:
                raise ValidationError('El certificado es obligatorio')
            
            certificado = request.files['certificado']
            
            # Obtener usuario actual
            user = g.get('username')
            
            # Crear proveedor
            supplier = self.service.create_supplier(
                validated_data,
                certificado,
                user
            )
            
            # Serializar respuesta
            result = self.response_schema.dump(supplier)
            
            return success_response(
                data=result,
                message='Proveedor registrado exitosamente',
                status_code=201
            )
        
        except MarshmallowValidationError as e:
            return error_response(
                message='Error de validación',
                status_code=400,
                errors=e.messages
            )
    
    def get_all(self):
        """
        GET /api/v1/suppliers
        Obtiene todos los proveedores con paginación y filtros
        """
        # Obtener parámetros de búsqueda y filtros
        search = request.args.get('search', None)
        pais = request.args.get('pais', None)
        status = request.args.get('status', None)
        
        # Obtener query con filtros
        query = self.service.get_all_suppliers(search, pais, status)
        
        # Paginar
        result = paginate_query(query)
        
        # Serializar
        items = self.list_schema.dump(result['items'], many=True)
        
        return paginated_response(
            items=items,
            page=result['page'],
            per_page=result['per_page'],
            total=result['total'],
            message='Proveedores obtenidos exitosamente'
        )
    
    def get_one(self, supplier_id):
        """
        GET /api/v1/suppliers/<id>
        Obtiene un proveedor por ID
        """
        supplier = self.service.get_supplier(supplier_id)
        result = self.response_schema.dump(supplier)
        
        return success_response(
            data=result,
            message='Proveedor obtenido exitosamente'
        )
    
    def update(self, supplier_id):
        """
        PUT /api/v1/suppliers/<id>
        Actualiza un proveedor
        """
        try:
            # Validar datos
            form_data = request.form.to_dict()
            validated_data = self.update_schema.load(form_data)
            
            # Verificar si hay nuevo certificado
            certificado = request.files.get('certificado', None)
            
            # Obtener usuario actual
            user = g.get('username')
            
            # Actualizar
            supplier = self.service.update_supplier(
                supplier_id,
                validated_data,
                certificado,
                user
            )
            
            # Serializar
            result = self.response_schema.dump(supplier)
            
            return success_response(
                data=result,
                message='Proveedor actualizado exitosamente'
            )
        
        except MarshmallowValidationError as e:
            return error_response(
                message='Error de validación',
                status_code=400,
                errors=e.messages
            )
    
    def delete(self, supplier_id):
        """
        DELETE /api/v1/suppliers/<id>
        Elimina un proveedor (soft delete)
        """
        user = g.get('username')
        self.service.delete_supplier(supplier_id, user)
        
        return success_response(
            message='Proveedor eliminado exitosamente',
            status_code=200
        )
    
    def get_stats(self):
        """
        GET /api/v1/suppliers/stats
        Obtiene estadísticas de proveedores
        """
        total = self.service.get_suppliers_count()
        
        stats = {
            'total_suppliers': total,
            'timestamp': request.args.get('realtime', 'true') == 'true'
        }
        
        return success_response(
            data=stats,
            message='Estadísticas obtenidas exitosamente'
        )
    
    def get_certificate(self, supplier_id):
        """
        GET /api/v1/suppliers/<id>/certificate
        Obtiene el certificado asociado al proveedor
        """
        try:
            # Obtener información del certificado
            certificate_info = self.service.get_supplier_certificate(supplier_id)
            
            # Enviar el archivo
            return send_file(
                certificate_info['path'],
                mimetype=certificate_info['mime_type'],
                as_attachment=True,
                download_name=certificate_info['filename']
            )
        
        except FileNotFoundError as e:
            logger.error(f'Archivo de certificado no encontrado para proveedor {supplier_id}: {str(e)}')
            return error_response(
                message='Certificado no encontrado',
                status_code=404
            )
        except Exception as e:
            logger.error(f'Error al obtener certificado para proveedor {supplier_id}: {str(e)}')
            return error_response(
                message='Error al obtener el certificado',
                status_code=500
            )
