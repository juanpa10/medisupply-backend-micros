from flask import Blueprint
from .controller import create_manager_controller, assign_client_controller, create_client_controller, get_client_manager_controller, list_managers_controller, get_manager_by_email_controller, list_clients_controller
from app.core.auth.decorators import require_auth

managers_bp = Blueprint('managers', __name__)

managers_bp.route('/managers', methods=['POST'])(create_manager_controller)
managers_bp.route('/managers', methods=['GET'])(list_managers_controller)
# new endpoint to fetch manager by email and include linked clients
managers_bp.route('/managers/by-email/<path:email>', methods=['GET'])(get_manager_by_email_controller)
# Accept either numeric id or identification string as manager reference and require auth
managers_bp.route('/managers/<manager_ref>/assign', methods=['POST', 'GET'])(require_auth(assign_client_controller))
# Protect client creation and lookup with authentication
managers_bp.route('/clients', methods=['POST'])(require_auth(create_client_controller))
managers_bp.route('/clients', methods=['GET'])(require_auth(list_clients_controller))
managers_bp.route('/clients/<int:client_id>/manager', methods=['GET'])(require_auth(get_client_manager_controller))
