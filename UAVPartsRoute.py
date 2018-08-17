#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:配件请求的响应
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
from UAVManagerDAO import PartsDao,UserDAO
from UAVManagerEntity import Parts
from datetime import datetime,date,time
parser = reqparse.RequestParser()
parser.add_argument('parts_id', type=int, location='args')
parser.add_argument('parts_ver',type=str,location='args')
parser.add_argument('parts_type',type=str,location='args')
parser.add_argument('parts_fact',type=str,location='args')
parser.add_argument('parts_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('parts_status',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

#配件列表url的请求与响应
class UAVPartsList(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            args = parser.parse_args()
            parts_status = args.get('parts_status')
            parts_type = args.get('parts_type')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            return self.dao.query_condition(user, None, None, parts_type, parts_status, page_index, page_size)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询所有配件的url请求与响应
class UAVPartsAll(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            return self.dao.query_all(user)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#根据配件id查询配件的请求与响应
class UAVPartsGetID(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            parts_id=data['parts_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)
            return self.dao.query_condition(user, parts_id, None, None, None, 1, 1)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询配件总页数url的请求与响应
class UAVPartsListPages(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            args = parser.parse_args()
            parts_status = args.get('parts_status')
            parts_type = args.get('parts_type')
            page_size = args.get('page_size')
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)
            return self.dao.query_pages(user,parts_type,parts_status,page_size)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询配件类别url的请求与响应
class UAVPartsTypes(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs=self.dao.query_type()
            return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询配件状态的统计信息url的请求与响应
class UAVPartsStatistic(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self,parts_status):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs=self.dao.query_statistic(user,parts_status)
            if rs==None:
                return make_response(jsonify({'error': '获取配件统计信息失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self,parts_status):
        return self.post(parts_status)

#添加配件的url的请求与响应
class UAVPartsAdd(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            parts= data['parts']
            parts_dict=json.loads(json.dumps(parts))
            parts_obj = Parts()
            parts_obj.parts_id = parts_dict[0]['parts_id']
            parts_obj.parts_ver = parts_dict[0]['parts_ver']
            parts_obj.parts_type = parts_dict[0]['parts_type']
            parts_obj.parts_fact = parts_dict[0]['parts_fact']
            parts_obj.parts_date = datetime.strptime(parts_dict[0]['parts_date'],'%Y-%m-%d').date()
            parts_obj.user_team = parts_dict[0]['user_team']
            parts_obj.parts_use_dpartment=parts_dict[0]['use_department']
            parts_obj.parts_status = '在库'
            parts_obj.parts_use_number = 0
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs = self.dao.add_parts(user,parts_obj)
            if rs==1:
                return make_response(jsonify({'success': '添加设备成功'}), 200)
            elif rs==2030701:
                return make_response(jsonify({'existed': '添加的设备已经存在','error':rs}), 401)
            elif rs==2030702:
                return make_response(jsonify({'existed': '无权限添加设备','error':rs}), 401)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#修改配件信息url的请求与响应
class UAVPartsModify(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            parts= data['parts']
            parts_dict=json.loads(json.dumps(parts))
            parts_obj = Parts()
            parts_obj.parts_id = parts_dict[0]['parts_id']
            parts_obj.parts_ver = parts_dict[0]['parts_ver']
            parts_obj.parts_type = parts_dict[0]['parts_type']
            parts_obj.parts_fact = parts_dict[0]['parts_fact']
            parts_obj.parts_date = datetime.strptime(parts_dict[0]['parts_date'],'%Y-%m-%d').date()
            parts_obj.user_team = parts_dict[0]['user_team']
            parts_obj.parts_use_dpartment = parts_dict[0]['use_department']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)


            rs = self.dao.modify_parts(user,parts_obj)
            if rs==1:
                return make_response(jsonify({'success': '添加设备成功'}), 200)
            elif rs==2030801:
                return make_response(jsonify({'failed': '待修改的设备不存在','errorcode':rs}), 401)
            elif rs==2030802:
                return make_response(jsonify({'failed': '无权限添加设备','errorcode':rs}), 401)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询配件状态url的请求与响应
class UAVPartsStatus(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            parts_id = data['parts_id']
            status = data['status']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs = self.dao.modify_parts_status(user,parts_id,status)
            if rs==1:
                return make_response(jsonify({'success': '修改配件状态成功'}), 200)
            else:
                return make_response(jsonify({'error': '无权限修改配件状态','errorcode':rs}), 401)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()