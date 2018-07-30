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
from UAVManagerDAO import FaultReportDao,UserDAO
from UAVManagerEntity import FaultReport
from datetime import datetime

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
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            return self.dao.query(fpid)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

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
            report.fault_time = datetime.strptime(reportdict[0]['fault_time'],'%Y-%m-%d').date()
            report.fault_crash_position = reportdict[0]['fault_crash_position']
            report.fault_crash_desc = reportdict[0]['fault_crash_desc']
            report.fault_crash_operation = reportdict[0]['fault_crash_operation']
            report.fault_crash_damage = reportdict[0]['fault_crash_damage']
            report.fault_crash_electric = reportdict[0]['fault_crash_electric']
            report.fault_crash_around = reportdict[0]['fault_crash_around']


            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            if self.dao.update(user,report)==1:
                return make_response(jsonify({'success': 'Update success'}), 200)
            else:
                return make_response(jsonify({'error': 'Unauthorized update'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()