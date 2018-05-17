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
from UAVManagerDAO import BatteryDAO,UserDAO
from UAVManagerEntity import Battery

parser = reqparse.RequestParser()
parser.add_argument('battery_id', type=int, location='args')
parser.add_argument('battery_ver',type=str,location='args')
parser.add_argument('battery_type',type=str,location='args')
parser.add_argument('battery_fact',type=str,location='args')
parser.add_argument('battery_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('battery_status',type=str,location='args')
parser.add_argument('page_index',type=int,required=True,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            battery_status = args.get('battery_status')
            battery_type   = args.get('battery_type')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            return self.dao.query_condition(user, None, None, battery_type,battery_status,page_index, page_size)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.query_statistic_all(user)
            if rs == -1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.query_statistic(user,battery_status)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self,battery_status):
        return self.post(battery_status)


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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.query_type()
            return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


class UAVBatteryListPages(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            page_size = data['page_size']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_pages(user,page_size)

    def get(self):
        return self.post()


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
            battery_obj.battery_date = battery_dict[0]['battery_date']
            battery_obj.user_team = battery_dict[0]['user_team']
            battery_obj.battery_status = '在库'
            battery_obj.battery_use_number = 0
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.add_battery(user, battery_obj)
            if rs == 1:
                return make_response(jsonify({'success': 'add device success'}), 200)
            else:
                return make_response(jsonify({'failed': 'add device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_battery_status(user, battery_id, status)
            if rs == 1:
                return make_response(jsonify({'success': 'modify device status success'}), 200)
            else:
                return make_response(jsonify({'failed': 'modify device status failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UAVBatteryModify(Resource):
    def __init__(self):
        self.dao = BatteryDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
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
                battery_obj.battery_date = battery_dict[0]['battery_date']
                battery_obj.user_team = battery_dict[0]['user_team']
                user = self.userDao.verify_token(token, '')
                if (not user):
                    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

                rs = self.dao.modify_battery(user, battery_obj)
                if rs == 1:
                    return make_response(jsonify({'success': 'add device success'}), 200)
                else:
                    return make_response(jsonify({'failed': 'add device failed'}), 401)
            else:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_battery_status(user, battery_id, status)
            if rs == 1:
                return make_response(jsonify({'success': 'modify device status success'}), 200)
            else:
                return make_response(jsonify({'failed': 'modify device status failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()