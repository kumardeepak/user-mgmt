from flask import session, g
from configs import AppConfig
import logging
import bcrypt
from datetime import datetime

from pymongo.errors import ConnectionFailure
from models import UserAdmin

class UserAdminRepositories:
    
    @staticmethod
    def is_user_registered(user):
        db      = g.db_client[AppConfig.get_database_name()]
        users   = db.users
        try:
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
        if UserAdminRepositories.is_user_registered(user):
            logging.debug('username [%s] with role [%s] already registered, cannot complete registration process' % (user.username, user.role))
            return False
        
        salt                = bcrypt.gensalt()
        hashed              = bcrypt.hashpw(user.password.encode('utf-8'), salt)
        user.salt           = salt    
        user.password       = hashed    
        db                  = g.db_client[AppConfig.get_database_name()]
        users               = db.users

        try:
            result = users.insert_one(user.to_dict(with_password=True))
        except ConnectionFailure as e:
                logging.error("db insert failed: " + str(e))
                return False
        return True

    @staticmethod
    def match(user):
        db      = g.db_client[AppConfig.get_database_name()]
        users   = db.users
        try:
            result = users.find_one({"username": user.username, "role": user.role})
            if result is not None and bcrypt.checkpw(user.password.encode('utf-8'), result['password']):
                logging.debug('username [%s] with role [%s] is verified' % (user.username, user.role))
            else:
                logging.debug('username [%s] with role [%s] could not be verified' % (user.username, user.role))
                return False
        except ConnectionFailure as e:
                logging.error("db insert failed: " + str(e))
                return False
        return True

