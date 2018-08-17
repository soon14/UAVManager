#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于借调申请的请求进行响应，通过Flask构建服务器解析请求
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
from UAVManagerDAO import ApprovalDao,UserDAO
from UAVManagerEntity import Approval

#查询所有借调申请的请求的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs=self.dao.approval_query(user)
            if rs==None:
                return make_response(jsonify({'error': '查询申请失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '传入参数错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#添加借调申请的请求的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs=self.dao.approval_add(user,approval)
            if rs==1:
                return make_response(jsonify({'success': '添加借调申请成功','errorcode':10000000}), 200)
            elif rs==2080601:
                return make_response(jsonify({'error': '批准人不存在','errorcode':rs}), 401)
            elif rs== 2080602 or rs==2080603:
                #批准人不存在
                return make_response(jsonify({'error': '批准人无批准权限','errorcode':rs}), 501)
        else:
            return  make_response(jsonify({'error': '输入参数错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#同意借调的请求的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)
            rs=self.dao.approval_aggree(user,approval)
            if rs==2080401:
                return make_response(jsonify({'error': '没有权限进行审批','errorcode':2080401}), 401)
            if rs==1:
                return make_response(jsonify({'success': '批准通过'}), 200)
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#拒绝借调的请求的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)


            rs=self.dao.approval_disagree(user,approval)
            if rs==2080501:
                return make_response(jsonify({'error': '没有权限进行审批','errorcode':rs}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误'}), 401)

    def get(self):
        return self.post()

#获取自己提交的申请的状态的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs=self.dao.approval_query_apply(user)
            if rs==None:
                return make_response(jsonify({'error': '查询申请失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误'}), 401)

    def get(self):
        return self.post()

#获取待我审批的申请的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 401)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 401)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 401)

            rs=self.dao.approval_query_approve(user)
            if rs==2080301:
                return make_response(jsonify({'error': '没有权限进行查询','errorcode':rs}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': '输入参数有误','errorcode':10000000}), 401)

    def get(self):
        return self.post()
