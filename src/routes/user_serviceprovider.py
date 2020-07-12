from flask import Blueprint
from flask_restful import Api
from resources.user_serviceprovider  import UserServiceProviderRegisterResource, UserServiceProviderLoginResource

USER_SERVICE_PROVIDER_BLUEPRINT      = Blueprint("user_service_provider", __name__)

Api(USER_SERVICE_PROVIDER_BLUEPRINT).add_resource(UserServiceProviderLoginResource,         "/v1/operator/login")
Api(USER_SERVICE_PROVIDER_BLUEPRINT).add_resource(UserServiceProviderRegisterResource,      "/v1/admin/register/serviceprovider")
