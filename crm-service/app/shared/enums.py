"""
Enumeraciones compartidas
"""
from enum import Enum


class Country(str, Enum):
    """Países"""
    COLOMBIA = 'Colombia'
    MEXICO = 'México'
    ARGENTINA = 'Argentina'
    CHILE = 'Chile'
    PERU = 'Perú'
    BRASIL = 'Brasil'
    ECUADOR = 'Ecuador'
    VENEZUELA = 'Venezuela'
    PANAMA = 'Panamá'
    COSTA_RICA = 'Costa Rica'
    HONDURAS = 'Honduras'
    GUATEMALA = 'Guatemala'
    EL_SALVADOR = 'El Salvador'
    NICARAGUA = 'Nicaragua'
    URUGUAY = 'Uruguay'
    PARAGUAY = 'Paraguay'
    BOLIVIA = 'Bolivia'
    CANADA = 'Canadá'
    USA = 'Estados Unidos'
    ESPANA = 'España'
    
    @classmethod
    def list(cls):
        """Retorna lista de países"""
        return [country.value for country in cls]


class Status(str, Enum):
    """Estados generales"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING = 'pending'
    SUSPENDED = 'suspended'
    
    @classmethod
    def list(cls):
        """Retorna lista de estados"""
        return [status.value for status in cls]


class FileType(str, Enum):
    """Tipos de archivo"""
    PDF = 'pdf'
    JPG = 'jpg'
    JPEG = 'jpeg'
    PNG = 'png'
    TXT = 'txt'
    
    @classmethod
    def list(cls):
        """Retorna lista de tipos de archivo"""
        return [file_type.value for file_type in cls]


class AuditAction(str, Enum):
    """Acciones de auditoría"""
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    RESTORE = 'restore'
    VIEW = 'view'
    EXPORT = 'export'
    
    @classmethod
    def list(cls):
        """Retorna lista de acciones"""
        return [action.value for action in cls]
