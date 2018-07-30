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
from PowerLineDao import DataServiceDao,UserDAO
from UAVManagerEntity import DataService

parser = reqparse.RequestParser()
parser.add_argument('linename', type=str, location='args')
parser.add_argument('url',type=str,location='args')

class DataServiceAdd(Resource):
    def __init__(self):
        self.dao = DataServiceDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            linename = data['linename']
            urlLink = data['url']
            dataservice = DataService()
            dataservice.tb_dataservice_linename=linename
            dataservice.tb_dataservice_url = urlLink

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs=self.dao.dataservice_add(dataservice)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return make_response(jsonify({'success': 'Add dataservice access'}), 200)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class DataServiceDelete(Resource):
    def __init__(self):
        self.dao = DataServiceDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            serviceid = data['serviceid']

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.dao.dataservice_delete(serviceid)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return make_response(jsonify({'success': 'Delete dataservice access'}), 200)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class DataServiceSearch(Resource):
    def __init__(self):
        self.dao = DataServiceDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            linename = data['linename']

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user == -1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            rs = self.dao.dataservice_search(linename)
            if rs == None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

