#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
from flask_restful import Resource
from flask_restful import reqparse
from flask import Flask, request ,jsonify
from flask import Response,make_response
from UAVManagerDAO import UserDAO
from UAVManagerEntity import User

class UserList(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            rs=self.dao.query_users(user)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)
    
    def get(self):
        return self.post()
        
class UserAdd(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            userAdddict = data['user']
            userAdd = User()
            userAdd.user_id = userAdddict[0]['user_id']
            userAdd.user_password = userAdddict[0]['user_password']
            userAdd.user_phone = userAdddict[0]['user_phone']
            userAdd.user_team = userAdddict[0]['user_team']
            userAdd.user_role = userAdddict[0]['user_role']
            
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            rs=self.dao.insert_user(userAdd,user)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)
    
    def get(self):
        return self.post()