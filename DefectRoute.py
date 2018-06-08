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
from PowerLineDao import DefectDao,DefectLevelDao,DefectPartDao
from UAVManagerDAO import UserDAO
from UAVManagerEntity import User,Defect

class DefectLevel(Resource):
    def __init__(self):
        self.dao = DefectLevelDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_defect_level(None)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class DefectPart(Resource):
    def __init__(self):
        self.dao = DefectPartDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_defect_part(None)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()