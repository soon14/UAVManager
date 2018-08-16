#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:数据服务的请求进行响应，通过Flask构建服务器解析请求
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
from PowerLineDao import DataServiceDao,UserDAO
from UAVManagerEntity import DataService

parser = reqparse.RequestParser()
parser.add_argument('linename', type=str, location='args')
parser.add_argument('url',type=str,location='args')

#添加数据服务的请求的响应
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
            type = data['type']
            dataservice = DataService()
            dataservice.tb_dataservice_linename=linename
            dataservice.tb_dataservice_url = urlLink
            dataservice.tb_dataservice_type=type

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期','errorcode':10000000}), 401)
            if user==1010301:
                return make_response(jsonify({'error': '登录过期','errorcode':user}), 401)
            if user==1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)


            rs=self.dao.dataservice_add(dataservice)
            if rs==None:
                return make_response(jsonify({'error': '添加服务失败','errorcode':10000000}), 401)
            else:
                return make_response(jsonify({'success': '添加服务成功'}), 200)
        else:
            return  make_response(jsonify({'error': '没有登录，无权限添加服务','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#修改数据服务的请求的解析和响应
class DataServiceModify(Resource):
    def __init__(self):
        self.dao = DataServiceDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            id=data['id']
            linename = data['linename']
            urlLink = data['url']
            type = data['type']
            dataservice = DataService()
            dataservice.tb_dataservice_linename=linename
            dataservice.tb_dataservice_url = urlLink
            dataservice.tb_dataservice_type=type

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期','errorcode':10000000}), 401)
            if user==1010301:
                return make_response(jsonify({'error': '登录过期','errorcode':user}), 401)
            if user==1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)


            rs=self.dao.dataservice_modify(id,linename,urlLink,type)
            if rs==None:
                return make_response(jsonify({'error': '添加服务失败','errorcode':10000000}), 401)
            else:
                return make_response(jsonify({'success': '添加服务成功'}), 200)
        else:
            return  make_response(jsonify({'error': '没有登录，无权限添加服务','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#删除数据服务请求的响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期','errorcode':10000000}), 401)
            if user==1010301:
                return make_response(jsonify({'error': '登录过期','errorcode':user}), 401)
            if user==1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs = self.dao.dataservice_delete(serviceid)
            if rs == None:
                return make_response(jsonify({'error': '删除服务失败','errorcode':10000000}), 401)
            else:
                return make_response(jsonify({'success': '删除服务成功'}), 200)
        else:
            return make_response(jsonify({'error': '没有登录，无权限删除服务', 'errorcode': 10000000}), 401)

    def get(self):
        return self.post()

#查询数据服务的请求的响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期','errorcode':10000000}), 401)
            if user==1010301:
                return make_response(jsonify({'error': '登录过期','errorcode':user}), 401)
            if user==1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs = self.dao.dataservice_search(linename)
            if rs == None:
                return make_response(jsonify({'error': '查询数据服务失败', 'errorcode': 10000000}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': '没有登录，无权限查询服务', 'errorcode': 10000000}), 401)

    def get(self):
        return self.post()

#查询存在数据服务的线路的请求与响应
class DataServiceSearchLine(Resource):
    def __init__(self):
        self.dao = DataServiceDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期','errorcode':10000000}), 401)
            if user==1010301:
                return make_response(jsonify({'error': '登录过期','errorcode':user}), 401)
            if user==1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)


            rs = self.dao.dataservice_searchLine()
            if rs == None:
                return make_response(jsonify({'error': '查询线路服务失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': '没有登录，无权限查询服务'}), 401)

    def get(self):
        return self.post()