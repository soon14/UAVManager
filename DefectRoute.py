#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于缺陷信息请求进行响应，通过Flask构建服务器解析请求
compiler:python2.7.x

created by  : Frank.Wu
company     : GEDI
created time: 2018.08.16
version     : version 1.0.0.0
"""

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
parser = reqparse.RequestParser()
parser.add_argument('tower_id', type=int, location='args')
parser.add_argument('photo_id', type=int, location='args')

#查询缺陷等级的请求的响应请求与响应
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
            return make_response(jsonify({'error': '查询缺陷等级失败','errorcode' : 10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#查询缺陷部位的请求与响应请求与响应
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
            return make_response(jsonify({'error': '查询缺陷部位失败','errorcode' : 10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据杆塔id查询杆塔的故障信息请求与响应
class DefectTowerID(Resource):
    def __init__(self):
        self.dao = DefectDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        towerid = args.get('tower_id')
        rs=self.dao.query_defect_tower(None,towerid)
        if rs==None:
            return make_response(jsonify({'error': '查询杆塔故障信息失败','errorcode' : 10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据照片id查询故障信息请求与响应
class DefectPhotoID(Resource):
    def __init__(self):
        self.dao = DefectDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        photo_id = args.get('photo_id')
        rs=self.dao.query_photo_id(None,photo_id)
        if rs==None:
            return make_response(jsonify({'error': '根据照片查询故障信息失败','errorcode' : 10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#故障信息的添加请求与响应
class DefectAdd(Resource):
    def __init__(self):
        self.dao = DefectDao()

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
            if rs==None:
                return make_response(jsonify({'error': '故障信息添加失败', 'errorcode': 10000000}), 401)
            else:
                return make_response(jsonify({'success': '添加故障成功'}), 200)
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据杆塔id和照片id查询照片信息请求与响应
class DefectPhotoIDSearch(Resource):
    def __init__(self):
        self.dao = DefectDao()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        towerid = args.get('tower_id')
        photoid = args.get('photo_id')
        rs=self.dao.query_defect_photo(None,photoid)
        if rs==None:
            return make_response(jsonify({'error': '根据照片id查询照片失败', 'errorcode': 10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()
