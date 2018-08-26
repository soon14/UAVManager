#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
desc:对于故障报告（炸机报告）操作请求进行响应，通过Flask构建服务器解析请求
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
from UAVManagerDAO import FaultReportDao,UserDAO
from UAVManagerEntity import FaultReport
from datetime import datetime

#查询炸机报告的请求解析与响应
class FaultReportQuery(Resource):
    def __init__(self):
        self.dao = FaultReportDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            fpid  = data['fault_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            return self.dao.query(fpid)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#更新修改炸机报告的请求解析与响应
class FaultReportUpdate(Resource):
    def __init__(self):
        self.dao = FaultReportDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            report = data['report']
            reportdict=json.loads(json.dumps(report))
            report = FaultReport()
            report.fault_report_id = reportdict[0]['fault_report_id']
            report.fault_report_device_id = reportdict[0]['fault_report_device_id']
            report.fault_report_line_name = reportdict[0]['fault_report_line_name']
            report.fault_report_towerRange = reportdict[0]['fault_report_towerRange']
            report.fault_report_date = datetime.strptime(reportdict[0]['fault_report_date'],'%Y-%m-%d').date()
            report.fault_report_flyer = reportdict[0]['fault_report_flyer']
            report.fault_report_wether = reportdict[0]['fault_report_wether']
            report.fault_report_observer = reportdict[0]['fault_report_observer']
            #时间格式需要修改
            #report.fault_time = datetime.strptime(reportdict[0]['fault_time'],'%Y-%m-%d %H:%M').date()
            report.fault_time = reportdict[0]['fault_time']
            report.fault_crash_position = reportdict[0]['fault_crash_position']
            report.fault_crash_desc = reportdict[0]['fault_crash_desc']
            report.fault_crash_operation = reportdict[0]['fault_crash_operation']
            report.fault_crash_damage = reportdict[0]['fault_crash_damage']
            report.fault_crash_electric = reportdict[0]['fault_crash_electric']
            report.fault_crash_around = reportdict[0]['fault_crash_around']

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            if self.dao.update(user,report)==1:
                return make_response(jsonify({'success': '更新炸机报告成功','errorcode':10000000}), 200)
            else:
                return make_response(jsonify({'error': '无权限更新炸机报告','errorcode':10000000}), 401)
        else:
            return make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()