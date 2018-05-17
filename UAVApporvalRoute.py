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
from UAVManagerDAO import ApprovalDao,UserDAO
from UAVManagerEntity import Approval

class UAVApprovalList(Resource):
    def __init__(self):
        self.dao = ApprovalDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.approval_query(user)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UAVApprovalAdd(Resource):
    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            approvaldict=data['approval']
            approval=Approval()
            approval.apply_person=approvaldict[0]['apply_person']
            approval.approval_team = approvaldict[0]['approval_team']
            approval.device_ver = approvaldict[0]['device_ver']
            approval.device_number = approvaldict[0]['device_number']
            approval.battery_ver = approvaldict[0]['battery_ver']
            approval.battery_number = approvaldict[0]['battery_number']
            approval.pad_ver = approvaldict[0]['pad_ver']
            approval.pad_number = approvaldict[0]['pad_number']
            approval.approval_status = 0

            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)

            rs=self.dao.approval_add(user,approval)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()