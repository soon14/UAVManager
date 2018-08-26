#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于巡检计划数据数据收到发送给服务器的请求，并对请求进行响应，通过Flask构建服务器解析请求
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
from UAVManagerDAO import PlanDao,UserDAO
from UAVManagerEntity import Battery
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('linename', type=str, location='args')
parser.add_argument('team',type=str,location='args')
parser.add_argument('datest',type=str,location='args')
parser.add_argument('dateend',type=str,location='args')

class UAVPlanSearch(Resource):
    def __init__(self):
        self.dao = PlanDao()
        self.userDao = UserDAO()

    def post(self):
        args = parser.parse_args()
        linename = args.get('linename')
        team   = args.get('team')
        datest = args.get('datest')
        dateend = args.get('dateend')
        return self.dao.searchPlan(linename,team,datest,dateend)

    def get(self):
        return self.post()