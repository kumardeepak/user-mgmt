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

from repositories import UserAdminRepositories
from models import UserAdmin

def check_username_format(id):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex, id)):
        return id
    else:
        logging.debug("username [%s] is not a valid email" % (id))
        raise ValueError("username {} is not valid email address".format(id))

user_parser         = reqparse.RequestParser(bundle_errors=True)
user_parser.add_argument('username',                 location='json', type=check_username_format, help='Please provide valid email address', required=True)
user_parser.add_argument('password',                 location='json', type=str, help='Password cannot be empty', required=True)

user_parser.add_argument('role',                     location='json', type=str, help='Please choose appropriate role', required=False)
user_parser.add_argument('first_name',               location='json', type=str, help='Please provide firstname', required=False)
user_parser.add_argument('last_name',                location='json', type=str, help='Please provide lastname', required=False)

class UserAdminRegisterResource(Resource):
    def post(self):
        args        = user_parser.parse_args()
        user        = UserAdmin(args)
        user.role   = user.get_role()

        if UserAdminRepositories.register(user):
            logging.debug('username [%s] with role [%s] is now registered successfully' % (user.username, user.role))
            return API.response(STATUS_CODES.SUCCESS_USER_REGISTERED, {})
        else:
            logging.error('username [%s] with role [%s] is not registered' % (user.username, user.role))
            return API.response(STATUS_CODES.ERROR_USER_ALREADY_REGISTERED, {})


class UserAdminLoginResource(Resource):
    def post(self):
        args            = user_parser.parse_args()
        user            = UserAdmin(args)
        user.role       = user.get_role()
        
        if UserAdminRepositories.match(user):
            logging.debug('username [%s] with role [%s] is now logged-in successfully' % (user.username, user.role))

            access_token    = create_access_token({'username': user.username, 'role': user.role})
            refresh_token   = create_access_token({'username': user.username, 'role': user.role})
            access_jti      = get_jti(encoded_token=access_token)
            refresh_jti     = get_jti(encoded_token=refresh_token)

            try:
                revoked_store   = redis.StrictRedis(host=AppConfig.get_redis_hostname(), port=AppConfig.get_redis_port(), db=0, decode_responses=True)
                revoked_store.set(access_jti,  'true', timedelta(minutes=AppConfig.get_jwt_access_token_expiry_in_mins()) * 1.2)
                revoked_store.set(refresh_jti, 'true', timedelta(days=AppConfig.get_jwt_refresh_token_expiry_in_days()) * 1.2)
            except Exception as e:
                logging.error('connection redis failed with :%s, cannot login user' % (e))
                logging.error('username [%s] with role [%s] is not logged-in' % (user.username, user.role))
                return API.response(STATUS_CODES.ERROR_LOGIN_FAILED_SYSTEM_ERROR, {})

            res             = { 'access_token': access_token, 'refresh_token': refresh_token }
            return API.response(STATUS_CODES.SUCCESS_USER_LOGGED_IN, res)
        else:
            logging.error('username [%s] with role [%s] is not logged-in' % (user.username, user.role))
            return API.response(STATUS_CODES.ERROR_USER_ALREADY_REGISTERED, {})

