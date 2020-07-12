from flask import session, g
from configs import AppConfig
import logging

from pymongo.errors import ConnectionFailure
import uuid
from datetime import datetime
from models import UserServiceProvider

class UserServiceProviderRepositories:
    
    @staticmethod
    def is_user_registered(user, with_app_key=False):
        db      = g.db_client[AppConfig.get_database_name()]
        users   = db.users
        try:
            if with_app_key:
                result = users.find_one({"app_key": user.app_key, "app_secret": user.app_secret, "role": user.role})
            else:
                result = users.find_one({"username": user.username, "role": user.role})

            if result is not None :
                return True
            else:
                return False
        except ConnectionFailure as e:
                logging.error("db insert failed: " + str(e))
                return False
        return True

    @staticmethod
    def register(user):
        if UserServiceProviderRepositories.is_user_registered(user):
            logging.debug('username [%s] with role [%s] already registered, cannot complete registration process' % (user.username, user.role))
            return False, None

        user.app_key        = str(uuid.uuid4())
        user.app_secret     = str(uuid.uuid4())
        db                  = g.db_client[AppConfig.get_database_name()]
        users               = db.users
        try:
            result = users.insert_one(user.to_dict())
        except ConnectionFailure as e:
                logging.error("db insert failed: " + str(e))
                return False, None
        return True, user

    @staticmethod
    def match(user):
        db      = g.db_client[AppConfig.get_database_name()]
        users   = db.users
        try:
            result = users.find_one({"app_key": user.app_key, "app_secret": user.app_secret})
            if result is not None and result['app_key'] == user.app_key:
                logging.debug('username [%s] with app_key [%s] logged-in successfully' % (result['username'], result['app_key']))
                return True, result
            else:
                logging.debug('app_key [%s] with app_secret [%s] could not be verified' % (user.app_key, user.app_secret))
                return False, None
        except ConnectionFailure as e:
                logging.error("db insert failed: " + str(e))
                return False, None
        return False, None
