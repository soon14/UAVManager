#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于平板数据收到发送给服务器的请求，并对请求进行响应，通过Flask构建服务器解析请求
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
from UAVManagerDAO import PadDao,UserDAO
from UAVManagerEntity import Pad
from datetime import datetime,date,time

parser = reqparse.RequestParser()
parser.add_argument('pad_id', type=int, location='args')
parser.add_argument('pad_ver',type=str,location='args')
parser.add_argument('pad_type',type=str,location='args')
parser.add_argument('pad_fact',type=str,location='args')
parser.add_argument('pad_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('pad_status',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

#查询平板列表的url请求解析与响应
class UAVPadList(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            pad_status = args.get('pad_status')
            pad_type = args.get('pad_type')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            return self.dao.query_condition(user, None, None, pad_type, pad_status, page_index, page_size)
        else:
            return
    def get(self):
        return self.post()

#查询所有平板的url请求解析与响应
class UAVPadAll(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_all(user)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    def get(self):
        return self.post()

#根据平板id查询平板的url请求解析与响应
class UAVPadGetID(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            pad_id = data['pad_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_condition(user, pad_id, None, None, None, 1, 1)

    def get(self):
        return self.post()

#平板数据分析请求的url解析与响应
class UAVPadListPages(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            args = parser.parse_args()
            pad_status = args.get('pad_status')
            pad_type = args.get('pad_type')
            page_size = args.get('page_size')
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_pages(user,pad_type,pad_status,page_size)

    def get(self):
        return self.post()

#查询平板类型请求url解析与响应
class UAVPadTypes(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_type()

    def get(self):
        return self.post()

#添加平板请求url解析与响应
class UAVPadAdd(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            pad= data['pad']
            pad_dict=json.loads(json.dumps(pad))
            pad_obj = Pad()
            pad_obj.pad_id = pad_dict[0]['pad_id']
            pad_obj.pad_ver = pad_dict[0]['pad_ver']
            pad_obj.pad_type = pad_dict[0]['pad_type']
            pad_obj.pad_fact = pad_dict[0]['pad_fact']
            pad_obj.pad_date = datetime.strptime(pad_dict[0]['pad_date'],'%Y-%m-%d').date()
            pad_obj.user_team = pad_dict[0]['user_team']
            pad_obj.pad_use_dpartment = pad_dict[0]['use_department']
            pad_obj.pad_status = '在库'
            pad_obj.pad_use_number = 0
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.add_pad(user,pad_obj)
            if rs==1:
                return make_response(jsonify({'success': 'add device success'}), 200)
            elif rs==-2:
                return make_response(jsonify({'existed': 'add device failed'}), 404)
            else:
                return make_response(jsonify({'failed': 'add device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#修改平板请求url解析与响应
class UAVPadModify(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            pad= data['pad']
            pad_dict=json.loads(json.dumps(pad))
            pad_obj = Pad()
            pad_obj.pad_id = pad_dict[0]['pad_id']
            pad_obj.pad_ver = pad_dict[0]['pad_ver']
            pad_obj.pad_type = pad_dict[0]['pad_type']
            pad_obj.pad_fact = pad_dict[0]['pad_fact']
            pad_obj.pad_date = datetime.strptime(pad_dict[0]['pad_date'],'%Y-%m-%d').date()
            pad_obj.user_team = pad_dict[0]['user_team']
            pad_obj.pad_use_dpartment = pad_dict[0]['use_department']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_pad(user,pad_obj)
            if rs==1:
                return make_response(jsonify({'success': 'add device success'}), 200)
            else:
                return make_response(jsonify({'failed': 'add device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#修改平板状态请求url解析与响应
class UAVPadStatus(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            pad_id = data['pad_id']
            status = data['status']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_pad_status(user,pad_id,status)
            if rs==1:
                return make_response(jsonify({'success': 'modify device status success'}), 200)
            else:
                return make_response(jsonify({'failed': 'modify device status failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#平板统计请求url解析与响应
class UAVPadsStatistic(Resource):
    def __init__(self):
        self.dao = PadDao()
        self.userDao = UserDAO()

    def post(self,pad_status):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.query_statistic(user,pad_status)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self,pad_status):
        return self.post(pad_status)