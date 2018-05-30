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
from UAVManagerDAO import DeviceDAO,UserDAO
from UAVManagerEntity import Device

parser = reqparse.RequestParser()
parser.add_argument('device_id', type=int, location='args')
parser.add_argument('device_ver',type=str,location='args')
parser.add_argument('device_type',type=str,location='args')
parser.add_argument('uad_code',type=str,location='args')
parser.add_argument('device_fact',type=str,location='args')
parser.add_argument('device_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('uad_camera',type=str,location='args')
parser.add_argument('uav_yuntai',type=str,location='args')
parser.add_argument('uad_rcontrol',type=str,location='args')
parser.add_argument('device_status',type=str,location='args')
parser.add_argument('page_index',type=int,required=True,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

#分页导出无人机
class UAVDeviceList(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            device_status = args.get('device_status')
            device_type   = args.get('device_type')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            return self.dao.query_condition(user, None, None, device_type, None, device_status, page_index, page_size)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UAVDeviceAll(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
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

#分页查询时查询总页数
class UAVDeviceListPages(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
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

#根据设备id查询无人机（设备id的参数在url中）
class UAVDeviceGetID(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def get(self,id):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            device_id = data['device_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                device_id = id
                return self.dao.query_condition(user,device_id,None,None,None,None,1,1)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def put(self,id):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            device = Device()
            device_data = request.data['device']
            args = parser.parse_args()
            device.device_id = id
            device.device_ver = device_data['device_ver']
            device.device_type = device_data['device_type']
            device.uad_code = device_data['uad_code']
            device.device_fact = device_data['device_fact']
            device.device_date = device_data['device_date']
            device.user_team = device_data['user_team']
            device.uad_camera = device_data['uad_camera']
            device.uav_yuntai = device_data['uav_yuntai']
            device.uad_rcontrol = device_data['uad_rcontrol']
            device.device_status = device_data['device_status']
            rs = dao.modify_device(user,device)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized modify'}), 401)
            else:
                return make_response(jsonify({'success': 'modify device success'}), 200)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def post(self,id):
        args = parser.parse_args()
        token = args.get('token')
        user = self.userDao.verify_token(token, '')
        if (not user):
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            device = Device()
            if (request.data != ""):
                data = json.loads(request.data)
                if not data.has_key('device'):
                    return make_response(jsonify({'error': 'Data Format Rrror'}), 401)
                device_data = request.data['device']
                device.device_id = device_data['device_id']
                device.device_ver = device_data['device_ver']
                device.device_type = device_data['device_type']
                device.uad_code = device_data['uad_code']
                device.device_fact = device_data['device_fact']
                device.device_date = device_data['device_date']
                device.user_team = device_data['user_team']
                device.uad_camera = device_data['uad_camera']
                device.uav_yuntai = device_data['uav_yuntai']
                device.uad_rcontrol = device_data['uad_rcontrol']
                device.device_status = device_data['device_status']
                rs=self.dao.add_device(user,device)
                if rs==1:
                    return make_response(jsonify({'success': 'add device success'}), 200)
                else:
                    return make_response(jsonify({'error': 'Unauthorized add data'}), 401)
            else:
                return make_response(jsonify({'error': 'Data Format Rrror'}), 401)

#出无人机设备统计图（设备状态的参数在url中）
class UAVDeviceManagerStatistic(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def post(self,status):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.query_statistic(user,status)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self,status):
        return self.post(status)

#无人机设备统计图（统计所有设备）
class UAVDeviceManagerStatisticList(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
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

#获取所有无人机类型
class UAVDeviceTypes(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
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

#获取所有无人机型号
class UAVDeviceVers(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.query_ver()
            return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#添加无人机
class UAVDeviceAdd(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            device_json= data['device']
            device_dict=json.loads(json.dumps(device_json))
            device_obj = Device()
            device_obj.device_id = int(device_dict[0]['device_id'])
            device_obj.device_ver = device_dict[0]['device_ver']
            device_obj.device_type = device_dict[0]['device_type']
            device_obj.uad_code = device_dict[0]['uad_code']
            device_obj.device_fact = device_dict[0]['device_fact']
            device_obj.device_date = device_dict[0]['device_date']
            device_obj.user_team = device_dict[0]['user_team']
            device_obj.uad_camera = device_dict[0]['uad_camera']
            device_obj.uav_yuntai = device_dict[0]['uav_yuntai']
            device_obj.uad_rcontrol = device_dict[0]['uad_rcontrol']
            device_obj.device_status = '在库'
            device_obj.device_use_number = 0

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.add_device(user,device_obj)
            if rs==1:
                return make_response(jsonify({'success': 'add device success'}), 200)
            else:
                return make_response(jsonify({'failed': 'add device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#修改无人机状态（参数早request data中）
class UAVDeviceStatus(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            device_id = data['device_id']
            status = data['status']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_device_status(user,device_id,status)
            if rs==1:
                return make_response(jsonify({'success': 'modify device status success'}), 200)
            else:
                return make_response(jsonify({'failed': 'modify device status failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#修改无人机情况（参数在request data中）
class UAVDeviceModify(Resource):
    def __init__(self):
        self.dao = DeviceDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            device_json= data['device']
            device_dict=json.loads(json.dumps(device_json))
            device_obj = Device()
            device_obj.device_id = int(device_dict[0]['device_id'])
            device_obj.device_ver = device_dict[0]['device_ver']
            device_obj.device_type = device_dict[0]['device_type']
            device_obj.uad_code = device_dict[0]['uad_code']
            device_obj.device_fact = device_dict[0]['device_fact']
            device_obj.device_date = device_dict[0]['device_date']
            device_obj.user_team = device_dict[0]['user_team']
            device_obj.uad_camera = device_dict[0]['uad_camera']
            device_obj.uav_yuntai = device_dict[0]['uav_yuntai']
            device_obj.uad_rcontrol = device_dict[0]['uad_rcontrol']

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_device(user,device_obj)
            if rs==1:
                return make_response(jsonify({'success': 'modify device success'}), 200)
            else:
                return make_response(jsonify({'failed': 'modify device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()