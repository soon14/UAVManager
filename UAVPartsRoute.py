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
from UAVManagerDAO import PartsDao,UserDAO
from UAVManagerEntity import Parts

parser = reqparse.RequestParser()
parser.add_argument('parts_id', type=int, location='args')
parser.add_argument('parts_ver',type=str,location='args')
parser.add_argument('parts_type',type=str,location='args')
parser.add_argument('parts_fact',type=str,location='args')
parser.add_argument('parts_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('parts_status',type=str,location='args')
parser.add_argument('page_index',type=int,required=True,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            parts_status = args.get('parts_status')
            parts_type = args.get('parts_type')
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            return self.dao.query_condition(user, None, None, parts_type, parts_status, page_index, page_size)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_condition(user, parts_id, None, None, None, 1, 1)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#查询配件总页数
class UAVPartsListPages(Resource):
    def __init__(self):
        self.dao = PartsDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            page_size=data['page_size']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query_pages(user,page_size)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#查询配件类别
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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.query_type()
            return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#查询配件状态的统计信息
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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.query_statistic(user,parts_status)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self,parts_status):
        return self.post(parts_status)

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
            parts_obj.parts_date = parts_dict[0]['parts_date']
            parts_obj.user_team = parts_dict[0]['user_team']
            parts_obj.parts_status = '在库'
            parts_obj.parts_use_number = 0
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.add_parts(user,parts_obj)
            if rs==1:
                return make_response(jsonify({'success': 'add device success'}), 200)
            else:
                return make_response(jsonify({'failed': 'add device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#修改配件信息
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
            parts_obj.parts_date = parts_dict[0]['parts_date']
            parts_obj.user_team = parts_dict[0]['user_team']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_parts(user,parts_obj)
            if rs==1:
                return make_response(jsonify({'success': 'add device success'}), 200)
            else:
                return make_response(jsonify({'failed': 'add device failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs = self.dao.modify_parts_status(user,parts_id,status)
            if rs==1:
                return make_response(jsonify({'success': 'modify device status success'}), 200)
            else:
                return make_response(jsonify({'failed': 'modify device status failed'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()