from splent_framework.blueprints.base_blueprint import create_blueprint
from splent_framework.services.service_locator import register_service

from splent_io.splent_feature_admin.services import AdminService

admin_bp = create_blueprint(__name__)


def init_feature(app):
    register_service(app, "AdminService", AdminService)


def inject_context_vars(app):
    return {}
