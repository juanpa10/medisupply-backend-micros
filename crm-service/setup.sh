#!/bin/bash

echo "🚀 Iniciando configuración de CRM Service..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Crear directorios necesarios
echo -e "${YELLOW}📁 Creando directorios...${NC}"
mkdir -p uploads/certificates
mkdir -p logs

# Copiar .env.example a .env si no existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creando archivo .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado. Por favor, configura las variables de entorno.${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe.${NC}"
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🐍 Creando entorno virtual...${NC}"
    python -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado.${NC}"
else
    echo -e "${GREEN}✓ Entorno virtual ya existe.${NC}"
fi

# Activar entorno virtual
echo -e "${YELLOW}🔌 Activando entorno virtual...${NC}"
source venv/bin/activate

# Instalar dependencias
echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo -e "${GREEN}✓ Dependencias instaladas.${NC}"

# Verificar conexión a base de datos
echo -e "${YELLOW}🗄️  Verificando configuración de base de datos...${NC}"
echo -e "${GREEN}✓ Asegúrate de que PostgreSQL esté ejecutándose y la base de datos 'crm_db' exista.${NC}"

echo ""
echo -e "${GREEN}✅ Configuración completada!${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus configuraciones"
echo "2. Crea la base de datos PostgreSQL: CREATE DATABASE crm_db;"
echo "3. Ejecuta las migraciones: flask db upgrade"
echo "4. Inicia la aplicación: python run.py"
echo ""
