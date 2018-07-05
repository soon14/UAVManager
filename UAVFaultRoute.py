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
from UAVManagerDAO import FaultDao,UserDAO
from UAVManagerEntity import Fault
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('device_ver',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            args = parser.parse_args()
            page_index = args.get('page_index')
            page_size = args.get('page_size')
            device_ver = args.get('device_ver')
            return self.dao.query_list(user,device_ver,page_index,page_size)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            return self.dao.query_pages(user,device_ver,page_size)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            return self.dao.query_types()
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.query_statistics(user)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

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
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.add_fault(user,fault)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return make_response(jsonify({'success': 'Fault add success'}), 200)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UAVFaultFinished(Resource):
    def __init__(self):
        self.dao = FaultDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            fault_id=data['fault_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.finished_fault(user,fault_id)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return make_response(jsonify({'success': 'Fault finished success'}), 401)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()