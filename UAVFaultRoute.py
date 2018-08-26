#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于故障查询操作请求进行响应，通过Flask构建服务器解析请求
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
from UAVManagerDAO import FaultDao,UserDAO
from UAVManagerEntity import Fault
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('device_ver',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

#查询故障列表的请求与响应
class UAVFaultList(Resource):
    def __init__(self):
        self.dao = FaultDao()
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
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            device_ver = args.get('device_ver')
            return self.dao.query_list(user,device_ver,page_index,page_size)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询故障的总页数的请求与响应
class UAVFaultListPages(Resource):
    def __init__(self):
        self.dao = FaultDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            args = parser.parse_args()
            page_size = args.get('page_size')
            device_ver = args.get('device_ver')
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            return self.dao.query_pages(user,device_ver,page_size)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询故障设备类型的请求与响应
class UAVFaultDeviceVersion(Resource):
    def __init__(self):
        self.dao = FaultDao()
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

            return self.dao.query_types()
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询故障统计信息的请求与响应
class UAVFaultStatistics(Resource):
    def __init__(self):
        self.dao = FaultDao()
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

            rs=self.dao.query_statistics(user)
            if rs==None:
                return make_response(jsonify({'error': '查询统计信息失败','errorcode':1000000}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#故障添加的请求与响应
class UAVFaultAdd(Resource):
    def __init__(self):
        self.dao = FaultDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            faultdict=data['fault']
            fault=Fault()
            fault.device_id = faultdict[0]['device_id']
            fault.device_ver = faultdict[0]['device_ver']
            fault.fault_date = datetime.strptime(faultdict[0]['fault_date'],'%Y-%m-%d').date()
            fault.fault_reason = faultdict[0]['fault_reason']
            fault.fault_deal = faultdict[0]['fault_deal']
            fault.fault_finished = 0

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs=self.dao.add_fault(user,fault)
            if rs==2060601:
                return make_response(jsonify({'error': '设备不存在','errorcode':rs}), 401)
            elif rs==2060602:
                return make_response(jsonify({'success': '设备不处于在库状态无法添加故障','errorcode':rs}),401)
            elif rs==2060603 or rs==2060604:
                return make_response(jsonify({'success': '无权限添加故障', 'errorcode': rs}), 401)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#故障维修完成的请求与响应
class UAVFaultFinished(Resource):
    def __init__(self):
        self.dao = FaultDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            fault_list=data['fault_id']

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs=1
            for item in fault_list:
                rs=self.dao.finished_fault(user,item)
                if rs == 2060901:
                    return make_response(jsonify({'error': '设备不存在','errorcode':rs}), 401)

            if rs==2060901:
                return make_response(jsonify({'error': '设备不存在', 'errorcode': rs}), 401)
            else:
                return make_response(jsonify({'success': '错误处理成功'}), 200)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#设备报废的请求与响应
class UAVFaultScrap(Resource):
    def __init__(self):
        self.dao = FaultDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            fault_list = data['fault_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            rs = 1
            for item in fault_list:
                rs = self.dao.scrap_fault(user, item)
                if rs == 2061001:
                    return make_response(jsonify({'error': '报废设备不存在','errorcode':rs}), 401)
                elif rs==2060801:
                    return make_response(jsonify({'error': '报废设备不存在', 'errorcode': rs}), 401)
            if rs == -1:
                return make_response(jsonify({'error': '报废设备不存在', 'errorcode': rs}), 401)
            else:
                return make_response(jsonify({'success': '报废处理成功'}), 200)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()