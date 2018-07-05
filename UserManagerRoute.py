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

parser = reqparse.RequestParser()
parser.add_argument('department', type=str, location='args')
parser.add_argument('team',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,location='args')

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
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            args = parser.parse_args()
            department = args.get('department')
            team   = args.get('team')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            rs=self.userDao.query_users(user,department,team,page_index,page_size)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)
    
    def get(self):
        return self.post()

class UserGetID(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user_id=data['user_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs = self.userDao.get_user_byId(user_id)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class DelUserID(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user_id = data['user_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs = self.userDao.delete_user_byId(user,user_id)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UserPages(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            args = parser.parse_args()
            department = args.get('department')
            team = args.get('team')
            page_size = args.get('page_size')
            rs = self.userDao.query_users_pages(user, department, team, page_size)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

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
            userAdd.user_name = userAdddict[0]['user_name']
            userAdd.user_number = userAdddict[0]['user_number']
            userAdd.user_department = userAdddict[0]['user_department']
            userAdd.user_team = userAdddict[0]['user_team']
            userAdd.user_role = userAdddict[0]['user_role']
            
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs=self.userDao.insert_user(userAdd,user)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif rs==-2:
                return make_response(jsonify({'error': 'User existed'}), 400)
            else:
                return make_response(jsonify({'success': 'add user success'}), 200)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)
    
    def get(self):
        return self.post()

class UserModify(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            userModifydict = data['user']
            userModify = User()
            userModify.user_id = userModifydict[0]['user_id']
            userModify.user_password = userModifydict[0]['user_password']
            userModify.user_phone = userModifydict[0]['user_phone']
            userModify.user_name = userModifydict[0]['user_name']
            userModify.user_number = userModifydict[0]['user_number']
            userModify.user_department = userModifydict[0]['user_department']
            userModify.user_team = userModifydict[0]['user_team']
            userModify.user_role = userModifydict[0]['user_role']

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.userDao.modify_user(userModify, user)
            if rs == -1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif rs == -2:
                return make_response(jsonify({'error': 'User existed'}), 400)
            else:
                return make_response(jsonify({'success': 'add user success'}), 200)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UserRole(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.userDao.get_role_type(user)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UserDepartment(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.userDao.get_role_department(user)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UserTeam(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.userDao.get_role_team(user)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UserTeams(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.userDao.get_role_teams()
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class TeamManager(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.userDao.get_teamManager(user)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()