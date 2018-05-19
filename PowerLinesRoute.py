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
from PowerLineDao import LinesDao, TowerDao,PhotoDao
from UAVManagerDAO import UserDAO
from UAVManagerEntity import User
parser = reqparse.RequestParser()
parser.add_argument('voltage', type=str, location='args')
parser.add_argument('linename', type=str, location='args')
parser.add_argument('towerid', type=int, location='args')
parser.add_argument('lineid', type=int, location='args')
class PowerLineListRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_lines()
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        lineid = args.get('lineid')
        rs=self.dao.query_line(lineid)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return json.dumps(rs)
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineTypeRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_lineTypes()
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineVoltageRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        voltage = args.get('voltage')
        rs=self.dao.query_lineVoltage(voltage)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


class PowerLineTowerRoute(Resource):
    def __init__(self):
        self.dao = TowerDao()
        self.userDao = UserDAO

    def post(self):
        # if (request.data != ""):
        #     data = json.loads(request.data)
        #     token = data['token']
        #     user = self.userDao.verify_token(token, '')
        #     if (not user):
        #          return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        linename = args.get('linename')
        rs=self.dao.query_towers(linename)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
        #     else:
        #         return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PwoerLinePhotoIdxRoute(Resource):
    def __init__(self):
        self.dao = PhotoDao()
        self.userDao = UserDAO

    def post(self):
        # if (request.data != ""):
        #     data = json.loads(request.data)
        #     token = data['token']
        #     toweridx = data['toweridx']
        #     user = self.userDao.verify_token(token, '')
        #     if (not user):
        #          return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        lineidx = args.get('towerid')
        rs=self.dao.query_photos(lineidx)
        if rs==None:
             return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

