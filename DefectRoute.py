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

parser.add_argument('tower_id', type=int, location='args')
parser.add_argument('photo_id', type=int, location='args')

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

class DefectTowerID(Resource):
    def __init__(self):
        self.dao = DefectPartDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        towerid = args.get('tower_id')
        rs=self.dao.query_defect_tower(towerid)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class DefectPhotoID(Resource):
    def __init__(self):
        self.dao = DefectPartDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        photo_id = args.get('photo_id')
        rs=self.dao.query_photo_id(photo_id)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class DefectAdd(Resource):
    def __init__(self):
        self.dao = DefectPartDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        if (request.data != ""):
            data = json.loads(request.data)
            strDefect=data['defect']
            defect = Defect()
            defect.tb_defect_photoid = strDefect[0]['photo_id']
            defect.tb_defect_lineid = strDefect[0]['line_id']
            defect.tb_defect_towerid = strDefect[0]['tower_id']
            defect.tb_defect_part = strDefect[0]['defect_part']
            defect.tb_defect_level=strDefect[0]['defect_level']
            defect.tb_defect_desc = strDefect[0]['defect_desc']

            rs=self.dao.defect_add(defect)
            if rs==-1:
                return make_response(jsonify({'error': 'add defect error'}), 401)
            else:
                return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()