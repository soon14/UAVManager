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
from PowerLineDao import LinesDao, TowerDao
from UAVManagerDAO import UserDAO
from UAVManagerEntity import User

class PowerLineListRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            rs=self.dao.query_lines()
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return post(self)

class PowerLineTowerRoute(Resource):
    def __init__(self):
        self.dao = TowerDao()
        self.userDao = UserDAO

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            lineIdx = data['lineID']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            rs=self.dao.query_towers()
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return post(self)

class PwoerLinePhotoIdxRoute(Resource):
    def __init__(self):
        self.dao = PhotoDao()
        self.userDao = UserDAO

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            toweridx = data['toweridx']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            rs=self.dao.query_towers(toweridx)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return post(self)
