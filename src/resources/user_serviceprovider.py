import redis
from datetime import timedelta
from flask_restful import fields, marshal_with, reqparse, Resource
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, get_jti,
    jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt
)

import os
from configs import AppConfig
import logging
import json
import re
import apiresponse as API
from apiresponse import status_codes as STATUS_CODES

from repositories import UserServiceProviderRepositories
from models import UserServiceProvider

def check_username_format(id):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex, id)):
        return id
    else:
        logging.debug("username [%s] is not a valid email" % (id))
        raise ValueError("username {} is not valid email address".format(id))

login_parser            = reqparse.RequestParser(bundle_errors=True)
login_parser.add_argument('app_key',                    location='json', type=str, help='app_key field cannot be empty', required=True)
login_parser.add_argument('app_secret',                 location='json', type=str, help='app_secret field cannot be empty', required=True)
login_parser.add_argument('role',                       location='json', type=str, help='', required=False)


register_parser         = reqparse.RequestParser(bundle_errors=True)
register_parser.add_argument('username',                location='json', type=check_username_format, help='Please provide valid email address', required=False)
register_parser.add_argument('role',                    location='json', type=str, help='Please choose appropriate role', required=False)
register_parser.add_argument('first_name',              location='json', type=str, help='Please provide firstname', required=False)
register_parser.add_argument('last_name',               location='json', type=str, help='Please provide lastname', required=False)
register_parser.add_argument('contact_mobile_number',   location='json', type=str, help='Please provide mobile number of user', required=False)
register_parser.add_argument('contact_email_address',   location='json', type=str, help='Please provide email address of user', required=False)
register_parser.add_argument('address',                 location='json', type=str, help='Please provide postal address', required=False)
register_parser.add_argument('country',                 location='json', type=str, help='Please provide country information', required=False)
register_parser.add_argument('state',                   location='json', type=str, help='Please provide state information', required=False)
register_parser.add_argument('zip_code',                location='json', type=str, help='Please provide zip code information', required=False)
register_parser.add_argument('app_key',                 location='json', type=str, help='app_key field cannot be empty', required=False)
register_parser.add_argument('app_secret',              location='json', type=str, help='app_secret field cannot be empty', required=False)

class UserServiceProviderRegisterResource(Resource):
    @jwt_required
    def post(self):
        args                        = register_parser.parse_args()
        user                        = UserServiceProvider(args)
        user.role                   = user.get_role()
        status, service_provider    = UserServiceProviderRepositories.register(user)
        
        if status:
            logging.debug('username [%s] with role [%s] is now registered successfully' % (user.username, user.role))
            return API.response(STATUS_CODES.SUCCESS_USER_REGISTERED, service_provider.to_dict())
        else:
            logging.error('username [%s] with role [%s] is not registered' % (user.username, user.role))
            return API.response(STATUS_CODES.ERROR_USER_ALREADY_REGISTERED, {})


class UserServiceProviderLoginResource(Resource):
    def post(self):
        args                        = login_parser.parse_args()
        user                        = UserServiceProvider(args, ignore_username=True)
        user.role                   = user.get_role()
        status, service_provider    = UserServiceProviderRepositories.match(user)
        if status:
            logging.debug('username [%s] app_key [%s] with role [%s] is now logged-in successfully' % (service_provider['username'], user.app_key, user.role))

            access_token    = create_access_token({'role': user.role, 'username': service_provider['username'], 'app_key': user.app_key})
            refresh_token   = create_access_token({'role': user.role, 'username': service_provider['username'], 'app_key': user.app_key})
            access_jti      = get_jti(encoded_token=access_token)
            refresh_jti     = get_jti(encoded_token=refresh_token)

            try:
                revoked_store   = redis.StrictRedis(host=AppConfig.get_redis_hostname(), port=AppConfig.get_redis_port(), db=0, decode_responses=True)
                revoked_store.set(access_jti,  'true', timedelta(minutes=AppConfig.get_jwt_access_token_expiry_in_mins()) * 1.2)
                revoked_store.set(refresh_jti, 'true', timedelta(days=AppConfig.get_jwt_refresh_token_expiry_in_days()) * 1.2)
            except Exception as e:
                logging.error('connection redis failed with :%s, cannot login user' % (e))
                logging.error('username [%s] with role [%s] is not logged-in' % (service_provider['username'], user.role))
                return API.response(STATUS_CODES.ERROR_LOGIN_FAILED_SYSTEM_ERROR, {})

            res             = { 'access_token': access_token, 'refresh_token': refresh_token }
            return API.response(STATUS_CODES.SUCCESS_USER_LOGGED_IN, res)
        else:
            logging.error('app_key [%s] with role [%s] is not logged-in' % (user.app_key, user.role))
            return API.response(STATUS_CODES.ERROR_USER_LOGIN, {})
