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

class FaultReportQuery(Resource):
    def __init__(self):
        self.dao = FaultReportDao()
        self.userDao = UserDAO()

        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            fpid  = data['fault_id']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            return self.dao.query(user,fpid)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class FaultReportUpdate(Resource):
    def __init__(self):
        self.dao = FaultReportDao()
        self.userDao = UserDAO()

        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            report = data['report']
            reportdict=json.loads(report)
            report = FaultReport()
            report.__dict__ = reportdict

            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if self.dao.update(user,report)==1:
                return make_response(jsonify({'success': 'Update success'}), 200)
            else:
                return make_response(jsonify({'error': 'Unauthorized update'}), 401)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()