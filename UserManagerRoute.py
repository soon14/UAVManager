#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于用户管理的请求进行响应，通过Flask构建服务器解析请求
compiler:python2.7.x

created by  : Frank.Wu
company     : GEDI
created time: 2018.08.16
version     : version 1.0.0.0
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
from flask_restful import Resource
from flask_restful import reqparse
from flask import Flask, request ,jsonify
from flask import Response,make_response
from UAVManagerDAO import UserDAO,UserLogDAO
from UAVManagerEntity import User
import datetime

parser = reqparse.RequestParser()
parser.add_argument('department', type=str, location='args')
parser.add_argument('starttime', type=str, location='args')
parser.add_argument('endtime', type=str, location='args')
parser.add_argument('team',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,location='args')

#查看用户列表的请求的解析与响应
class UserList(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            args = parser.parse_args()
            department = args.get('department')
            team   = args.get('team')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            rs=self.userDao.query_users(user,department,team,page_index,page_size)
            if rs==None:
                return make_response(jsonify({'error': '无权限查询用户信息','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)
    
    def get(self):
        return self.post()

#根据用户id获取用户的请求的解析㔿响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)


            rs = self.userDao.get_user_byId(user_id)
            if rs == None:
                return make_response(jsonify({'error': '无权限查询用户信息','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#根据用户id删除用的请求解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.delete_user_byId(user,user_id)
            if rs == None:
                return make_response(jsonify({'error': '无权限删除用户','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#用户数据总页数的请求解析与响应
class UserPages(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            args = parser.parse_args()
            department = args.get('department')
            team = args.get('team')
            page_size = args.get('page_size')
            rs = self.userDao.query_users_pages(user, department, team, page_size)
            if rs == None:
                return make_response(jsonify({'error': '用户无权限进行查询','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#添加用户的请求的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)


            rs=self.userDao.insert_user(userAdd,user)
            if rs==1010401 or rs==1010403:
                return make_response(jsonify({'error': '添加的用户已经存在','errorcode':rs}), 401)
            elif rs==1010402:
                return make_response(jsonify({'error': '无权限添加非本班组用户','errorcode':rs}), 401)
            elif rs==1010404:
                return make_response(jsonify({'success': '无权限添加用户','errorcode':rs}), 401)
            elif rs==1:
                return make_response(jsonify({'success': '添加用户成功'}), 200)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)
    
    def get(self):
        return self.post()

#修改用户的请求解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)


            rs = self.userDao.modify_user(userModify, user)
            if rs == 1010501 or rs==1010504:
                return make_response(jsonify({'error': '用户不存在','errorcode':rs}), 401)
            elif rs == 1010502 or rs ==1010503 or rs ==1010503:
                return make_response(jsonify({'error': '当前用户无权限进行修改','errorcode':rs}), 400)
            else:
                return make_response(jsonify({'success': '添加用户成功'}), 200)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#获取用户权限类别的请求解析与响应
class UserRole(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.get_role_type(user)
            if rs == None:
                return make_response(jsonify({'error': '获取权限类别失败','errorcode':rs}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询用户部门的请求解析与响应
class UserDepartment(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.get_role_department(user)
            if rs == None:
                return make_response(jsonify({'error': '没有权限获取用户部门信息','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询用户班组的请求解析与响应
class UserTeam(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.get_role_team(user)
            if rs == None:
                return make_response(jsonify({'error': '无权限获取用户班组信息','errorcode':1000000}), 401)
            else:
                #添加
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#分组查询所有用户的班组信息的请求解析与响应
class UserTeams(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.get_role_teams()
            if rs == None:
                return make_response(jsonify({'error': '无权限查询班组信息','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询用户所在班组的班组管理员姓名的请求与响应
class TeamManager(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.get_teamManager(user)
            if rs == None:
                return make_response(jsonify({'error': '获取班组管理员失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询当前登录用户所在班组中所有成员
class TeamUsers(Resource):
    def __init__(self):
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.userDao.get_teamUser(user)
            if rs == 1011501:
                return make_response(jsonify({'error': '获取班组管理员失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询用户统计信息
class UserLogStatistic(Resource):
    def __init__(self):
        self.logDao = UserLogDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            deparment=None
            sttiem   =None
            endtime  =None
            if(data['department'] != None):
                deparment = data['department']
            if(data['sttime'] != ""):
                sttiem    = datetime.datetime.strptime(data['sttime'] , '%Y-%m-%d').date()
            if(data['endtime']!=""):
                endtiem   = datetime.datetime.strptime(data['endtime'] , '%Y-%m-%d').date()

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = self.logDao.queryStatistic(deparment,sttiem,endtime)
            if rs == 1011501:
                return make_response(jsonify({'error': '获取登录日志信息失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()