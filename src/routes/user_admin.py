from flask import Blueprint
from flask_restful import Api
from resources.user_admin  import UserAdminLoginResource, UserAdminRegisterResource

USER_ADMIN_BLUEPRINT      = Blueprint("user_admin", __name__)

Api(USER_ADMIN_BLUEPRINT).add_resource(UserAdminLoginResource,         "/v1/admin/login")
Api(USER_ADMIN_BLUEPRINT).add_resource(UserAdminRegisterResource,      "/v1/admin/register")
