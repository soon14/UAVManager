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
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

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
    def __init__(self):
        self.dao = ApprovalDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            approvaldict=data['approval']
            approval=Approval()
            approval.apply_person=approvaldict[0]['apply_person']
            approval.approval_person = approvaldict[0]['approval_person']
            approval.approval_team = approvaldict[0]['approval_team']
            approval.device_ver = approvaldict[0]['device_ver']
            approval.device_number = approvaldict[0]['device_number']
            approval.battery_ver = approvaldict[0]['battery_ver']
            approval.battery_number = approvaldict[0]['battery_number']
            approval.pad_ver = approvaldict[0]['pad_ver']
            approval.pad_number = approvaldict[0]['pad_number']
            #approval.approval_reason = approvaldict[0]['reason']
            #approval.approval_desc = approvaldict[0]['desc']
            approval.approval_status = 0

            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.approval_add(user,approval)
            if rs==1:
                return make_response(jsonify({'success': 'Apply success'}), 200)
            elif rs==-1:
                return make_response(jsonify({'error': 'Apply failed'}), 401)
            elif rs==-2:
                #批准人不存在
                return make_response(jsonify({'error': 'Approver does not exist'}), 501)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UAVApprovalAgree(Resource):
    def __init__(self):
        self.dao = ApprovalDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')

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
            approval.approval_person = user.user_id
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.approval_aggree(user,approval)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if rs==1:
                return make_response(jsonify({'success': 'aggreed'}), 200)
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class UAVApprovalDisagree(Resource):
    def __init__(self):
        self.dao = ApprovalDao()
        self.userDao = UserDAO()

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

            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.approval_disagree(user,approval)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#获取自己提交的申请的状态
class UAVApprovalListApply(Resource):
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
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.approval_query_apply(user)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#获取待我审批的申请
class UAVApprovalListApprove(Resource):
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
            if user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)

            rs=self.dao.approval_query_approve(user)
            if rs==None:
                return []
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()
