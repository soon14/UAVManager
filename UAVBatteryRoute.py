#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于电池数据收到发送给服务器的请求，并对请求进行响应，通过Flask构建服务器解析请求
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
from UAVManagerDAO import BatteryDAO,UserDAO
from UAVManagerEntity import Battery
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('battery_id', type=int, location='args')
parser.add_argument('battery_ver',type=str,location='args')
parser.add_argument('battery_type',type=str,location='args')
parser.add_argument('battery_fact',type=str,location='args')
parser.add_argument('battery_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('battery_status',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,location='args')

#电池列表展示url请求与响应
class UAVBatteryList(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
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
            battery_status = args.get('battery_status')
            battery_type   = args.get('battery_type')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            return self.dao.query_condition(user, None, None, battery_type,battery_status,page_index, page_size)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#查询所有电池设备url请求与响应
class UAVBatteryAll(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
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
            return make_response(jsonify({'error': '输入参数有错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#根据设备id查询url的请求与响应
class UAVBatteryGetID(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            battery_id = data['battery_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)


            return self.dao.query_condition(user, battery_id, None, None,None,1, 1)
        else:
            return make_response(jsonify({'error': '输入数据有误','errorcode':1000000}), 401)

    def get(self):
        return self.post()

#查询所有电池统计信息url请求与响应
class UAVBatteryStatisticsList(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
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

            rs = self.dao.query_statistic_all(user)
            if rs == None:
                return make_response(jsonify({'error': '获取统计信息失败'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': '输入参数失败'}), 401)

    def get(self):
        return self.post()

#查询电池统计信息url请求与响应
class UAVBatteryStatistic(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self,battery_status):
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

            rs=self.dao.query_statistic(user,battery_status)
            if rs==-None:
                return make_response(jsonify({'error': '获取统计信息失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数错误','errorcode':10000000}), 401)

    def get(self,battery_status):
        return self.post(battery_status)

#查询电池的类型url请求与响应
class UAVBatteryTypes(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
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
            return  make_response(jsonify({'error': '输入参数错误'}), 401)

    def get(self):
        return self.post()

#根据电池的状态和类型查询电池分页的页数url请求与响应
class UAVBatteryListPages(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            args = parser.parse_args()
            battery_status = args.get('battery_status')
            battery_type   = args.get('battery_type')
            page_size = args.get('page_size')
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            return self.dao.query_pages(user,battery_type,battery_status,page_size)

    def get(self):
        return self.post()

#添加电池 成功则返回1  url请求与响应
class UAVBatteryAdd(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            battery = data['battery']
            battery_dict = json.loads(json.dumps(battery))
            battery_obj = Battery()
            battery_obj.battery_id = battery_dict[0]['battery_id']
            battery_obj.battery_ver = battery_dict[0]['battery_ver']
            battery_obj.battery_type = battery_dict[0]['battery_type']
            battery_obj.battery_fact = battery_dict[0]['battery_fact']
            battery_obj.battery_date = datetime.strptime(battery_dict[0]['battery_date'],'%Y-%m-%d').date()
            battery_obj.user_team = battery_dict[0]['user_team']
            battery_obj.battery_use_dpartment=battery_dict[0]['use_department']
            battery_obj.battery_status = '在库'
            battery_obj.battery_use_number = 0
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs = self.dao.add_battery(user, battery_obj)
            if rs == 1:
                return make_response(jsonify({'success': '添加电池成功'}), 200)
            elif rs==2020901:
                return make_response(jsonify({'existed': '待添加的电池已经存在，添加电池失败','errorcode':rs}), 404)
            else:
                return make_response(jsonify({'failed': '添加电池失败','errorcode':rs}), 401)
        else:
            return make_response(jsonify({'error': '输入参数错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#修改电池状态url请求与响应
class UAVBatteryStatus(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            battery_id = data['battery_id']
            status = data['status']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs = self.dao.modify_battery_status(user, battery_id, status)
            if rs == 1:
                return make_response(jsonify({'success': '修改电池状态成功'}), 200)
            else:
                return make_response(jsonify({'failed': '用户无权限修改电池状态','errorcode':rs}), 401)
        else:
            return make_response(jsonify({'error': '输入参数错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#修改电池信息url请求与响应
class UAVBatteryModify(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            if (request.data != ""):
                data = json.loads(request.data)
                token = data['token']
                battery = data['battery']
                battery_dict = json.loads(json.dumps(battery))
                battery_obj = Battery()
                battery_obj.battery_id = battery_dict[0]['battery_id']
                battery_obj.battery_ver = battery_dict[0]['battery_ver']
                battery_obj.battery_type = battery_dict[0]['battery_type']
                battery_obj.battery_fact = battery_dict[0]['battery_fact']
                battery_obj.battery_date = datetime.strptime(battery_dict[0]['battery_date'],'%Y-%m-%d').date()
                battery_obj.user_team = battery_dict[0]['user_team']
                battery_obj.battery_use_dpartment = battery_dict[0]['use_department']
                user = self.userDao.verify_token(token, '')
                if (not user):
                    return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
                if user == 1010301:
                    return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
                if user == 1010302:
                    return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

                rs = self.dao.modify_battery(user, battery_obj)
                if rs == 1:
                    return make_response(jsonify({'success': '修改电池状态成功'}), 200)
                elif rs==2021001:
                    return make_response(jsonify({'failed': '待修改的电池不存在','errorcode':rs}), 401)
            else:
                return make_response(jsonify({'error': '输入参数错误','errorcode':10000000}), 401)
    def get(self):
        return self.post()