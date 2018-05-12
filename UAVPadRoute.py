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
from UAVManagerDAO import PadDao,UserDAO
from UAVManagerEntity import Pad

parser = reqparse.RequestParser()
parser.add_argument('pad_id', type=int, location='args')
parser.add_argument('pad_ver',type=str,location='args')
parser.add_argument('pad_type',type=str,location='args')
parser.add_argument('pad_fact',type=str,location='args')
parser.add_argument('pad_date',type=str,location='args')
parser.add_argument('user_team',type=str,location='args')
parser.add_argument('pad_status',type=str,location='args')
parser.add_argument('page_index',type=int,required=True,location='args')
parser.add_argument('page_size',type=int,required=True,location='args')

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

    def get(self):
        return self.post()

class UAVPadListPages(Resource):
    def __init__(self):
        self.dao = PadDao()
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
