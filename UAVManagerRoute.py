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
from UAVManagerDAO import ManagerDAO,UserDAO,DeviceDAO

parser = reqparse.RequestParser()
parser.add_argument('device_id', type=int, location='args')
parser.add_argument('device_ver',type=str,location='args')
parser.add_argument('device_type',type=str,location='args')
parser.add_argument('manager_status',type=str,location='args')
parser.add_argument('borrow_time',type=str,location='args')
parser.add_argument('return_time',type=str,location='args')
parser.add_argument('token',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

class ManagerList(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def get(self):
        args = parser.parse_args()
        token = args.get('token')
        user = self.userDao.verify_token(token, '')
        if (not user):
             return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            rs=self.dao.query_all(user)
            return rs

class ManagerListPages(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            args = parser.parse_args()
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                args = parser.parse_args()
                device_type=args.get('device_type')
                device_status=args.get('device_status')
                device_version=args.get('device_ver')
                page_index = args.get('page_index')
                page_size = args.get('page_size')
                rs=self.dao.query_condition(user,device_version,None,device_type,device_status,None,None,page_index,page_size)
                return json.dumps(rs)
        else:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerListPageNum(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            page_size=data['page_size']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                args = parser.parse_args()
                device_type=args.get('device_type')
                device_status=args.get('device_status')
                device_ver=args.get('device_ver')
                page_size = args.get('page_size')
                rs=self.dao.query_pages(user,device_type,device_ver,device_status,page_size)
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerBorrow(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            borrowList=data['borrow']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                ret=[]
                for item in borrowList:
                    rs=self.dao.manager_borrow(user,item['approver'],item['borrower'],item['borrow_team'],item['uav_id'],item['borrow_time'],item['return_time'])
                    if rs==-1:
                        return make_response(jsonify({'error': 'borrower not exist'}), 401)
                    if rs==-2:
                        return make_response(jsonify({'error': 'device not returned'}), 404)

                    ret = self.dao.manager_query_device(int(item['uav_id']),item['return_time'],item['borrower'])
                return json.dumps(ret)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class ManagerReturn(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            borrowList=data['return']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:

                for item in borrowList:
                    rs=self.dao.manager_return(user,item['device_id'],item['return_date'],item['return_desc'])
                    if rs!=1:
                        return make_response(jsonify({'error': 'return deivce failed'}), 401)
                    ret = self.dao.manager_query_device(int(item['device_id']), item['return_date'],"")
                return json.dumps(ret)
        else:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)



