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
from UAVManagerDAO import ManagerDAO,UserDAO,DeviceDAO,Manager
from datetime import datetime,date,time

parser = reqparse.RequestParser()
parser.add_argument('device_id', type=int, location='args')
parser.add_argument('device_ver',type=str,location='args')
parser.add_argument('device_type',type=str,location='args')
parser.add_argument('device_status',type=str,location='args')
parser.add_argument('manager_status',type=str,location='args')
parser.add_argument('borrow_time',type=str,location='args')
parser.add_argument('return_time',type=str,location='args')
parser.add_argument('token',type=str,location='args')
parser.add_argument('page_index',type=int,location='args')
parser.add_argument('page_size',type=int,location='args')
parser.add_argument('start_time',type=str,location='args')
parser.add_argument('end_time',type=str,location='args')


class ManagerList(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def get(self):
        args = parser.parse_args()
        token = args.get('token')
        user = self.userDao.verify_token(token, '')
        if (not user):
             return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        elif user == -1:
            return make_response(jsonify({'error': 'token expired'}), 399)
        else:
            rs=self.dao.query_all(user)
            return rs

class ManagerListPages(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            args = parser.parse_args()
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                args = parser.parse_args()
                device_type=args.get('device_type')
                device_status=args.get('device_status')
                device_version=args.get('device_ver')
                page_index = args.get('page_index')
                page_size = args.get('page_size')
                rs=self.dao.query_device_manager(device_type,device_version,device_status,page_index,page_size)
                return rs
        else:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerListPageNum(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                args = parser.parse_args()
                device_type=args.get('device_type')
                device_status=args.get('device_status')
                device_ver=args.get('device_ver')
                page_size = args.get('page_size')
                rs=self.dao.query_pages(user,device_type,device_ver,device_status,page_size)
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerHistoryPages(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                args = parser.parse_args()
                page_size = args.get('page_size')
                rs=self.dao.query_history_pagenumber(user,page_size)
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerHistory(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                args = parser.parse_args()
                page_size = args.get('page_size')
                page_index = args.get('page_index')
                rs=self.dao.query_page(user,page_index,page_size)
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerHistorySearchPages(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                args = parser.parse_args()
                page_size = args.get('page_size')
                sttime = datetime.strptime(args.get('start_time'),'%Y-%m-%d').date()
                endtime=datetime.strptime(args.get('end_time'),'%Y-%m-%d').date()
                rs=self.dao.query_date_pagenumber(user,page_size,sttime,endtime)
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return (self.post())

class ManagerHistorySearch(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if not user:
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                args = parser.parse_args()
                page_size = args.get('page_size')
                page_index = args.get('page_index')
                sttime = datetime.strptime(args.get('start_time'),'%Y-%m-%d').date()
                endtime=datetime.strptime(args.get('end_time'),'%Y-%m-%d').date()
                rs=self.dao.query_time(user,page_index,page_size,sttime,endtime)
                return rs
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return(self.post())

class ManagerBorrow(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            borrowList=data['borrow']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                ret=[]
                borrower = borrowList['borrower']
                #borrowteam=borrowList['borrow_team']
                borrowtime = datetime.strptime(borrowList['borrow_time'], '%Y-%m-%d').date()
                returntime = None
                device_idList = borrowList['uav_id']

                #单次扫描的时候调用的
                #for item in borrowList:
                #    borrowtime=datetime.strptime(item['borrow_time'],'%Y-%m-%d').date()
                #    returntime = datetime.strptime(item['return_time'], '%Y-%m-%d').date()
                #    rs=self.dao.manager_borrow(user,item['borrower'],item['borrow_team'],item['uav_id'],borrowtime,returntime)
                #    if rs==-1:
                #        return make_response(jsonify({'error': 'device not exist'}), 401)
                #    if rs==-2:
                #        return make_response(jsonify({'error': 'device not returned'}), 404)
                #    if rs == -3:
                #        return make_response(jsonify({'error': 'borrower not returned'}), 405)
                #    if rs == -4:
                #        return make_response(jsonify({'error': 'approver not exist'}), 406)
                #    ret = self.dao.manager_query_device(int(item['uav_id']),returntime.strftime('%Y-%m-%d'),item['borrower'],'')
                #return json.dumps(ret)

                #同时借用多个，建议前端修改调用这个接口
                tmplist=[]
                for item in device_idList:
                #    borrowtime=datetime.strptime(item['borrow_time'],'%Y-%m-%d').date()
                #    returntime = datetime.strptime(item['return_time'], '%Y-%m-%d').date()
                    mngr = Manager()
                    mngr.borrow_date = borrowtime
                    mngr.return_date = returntime
                    mngr.device_id = item
                    mngr.borrower_name = borrower
                    tmplist.append(mngr)
                rs = self.dao.manager_borrowList(user,tmplist)
                if len(rs)==0:
                    return  make_response(jsonify({'error': 'device is borrowed or have no authority to borrow'}), 401)
                else:
                    return json.dumps(rs)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class ManagerBorrowConfirm(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            borrowList=data['borrow']
            if len(borrowList) <=0:
                return make_response(jsonify({'error': 'no borrow device'}), 401)
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                ret=[]
                for item in borrowList:
                    borrower   = item['borrower']
                    #borrowteam = item['team']
                    borrowtime = datetime.strptime(item['return_date'], '%Y-%m-%d').date()
                    returntime = datetime.strptime(item['return_date'], '%Y-%m-%d').date()
                    deviceid   = item['id']
                    rs=self.dao.manager_borrow(user,borrower,None,deviceid,borrowtime,returntime)
                    if rs==-1:
                        return make_response(jsonify({'error': 'device not exist'}), 401)
                    if rs==-2:
                        return make_response(jsonify({'error': 'device not returned'}), 404)
                    if rs == -3:
                        return make_response(jsonify({'error': 'borrower not returned'}), 405)
                    if rs == -4:
                        return make_response(jsonify({'error': 'approver not exist'}), 406)
                    #ret = self.dao.manager_query_device(int(item['uav_id']),returntime.strftime('%Y-%m-%d'),item['borrower'],'')
                return make_response(jsonify({'success': 'Borrow success'}), 200)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class ManagerReturn(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            returnList=data['return']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                ret=[]
                returntime = datetime.strptime(returnList['return_time'], '%Y-%m-%d').date()
                device_idList = returnList['uav_id']

                #单次扫描的时候调用的已经弃用了
                #for item in borrowList:
                #    borrowtime=datetime.strptime(item['borrow_time'],'%Y-%m-%d').date()
                #    returntime = datetime.strptime(item['return_time'], '%Y-%m-%d').date()
                #    rs=self.dao.manager_borrow(user,item['borrower'],item['borrow_team'],item['uav_id'],borrowtime,returntime)
                #    if rs==-1:
                #        return make_response(jsonify({'error': 'device not exist'}), 401)
                #    if rs==-2:
                #        return make_response(jsonify({'error': 'device not returned'}), 404)
                #    if rs == -3:
                #        return make_response(jsonify({'error': 'borrower not returned'}), 405)
                #    if rs == -4:
                #        return make_response(jsonify({'error': 'approver not exist'}), 406)
                #    ret = self.dao.manager_query_device(int(item['uav_id']),returntime.strftime('%Y-%m-%d'),item['borrower'],'')
                #return json.dumps(ret)

                #同时借用多个，建议前端修改调用这个接口
                tmplist=[]
                for item in device_idList:
                    mngr = Manager()
                    mngr.return_date = returntime
                    mngr.device_id = item
                    tmplist.append(mngr)
                rs = self.dao.manager_return_list(user,tmplist)
                if len(rs)==0:
                    return  make_response(jsonify({'error': 'device is borrowed or have no authority to borrow'}), 401)
                else:
                    return json.dumps(rs)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)

class ManagerReturnConfirm(Resource):
    def __init__(self):
        self.dao = ManagerDAO()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            returnList=data['return']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            elif user==-1:
                return make_response(jsonify({'error': 'token expired'}), 399)
            else:
                ret=[]
                for item in returnList:
                    returntime = datetime.strptime(item['return_date'], '%Y-%m-%d').date()
                    deviceid   = item['id']
                    device_cond= item['condition']
                    rs=self.dao.manager_return(user,deviceid,returntime,device_cond)
                    if rs==-1:
                        return make_response(jsonify({'error': 'device not exist'}), 401)
                    if rs==-2:
                        return make_response(jsonify({'error': 'device not returned'}), 404)
                    if rs == -3:
                        return make_response(jsonify({'error': 'borrower not returned'}), 405)
                    if rs == -4:
                        return make_response(jsonify({'error': 'approver not exist'}), 406)
                    if rs == -5:
                        return make_response(jsonify({'error': 'Unauthorized access'}), 401)
                    #ret = self.dao.manager_query_device(int(item['uav_id']),returntime.strftime('%Y-%m-%d'),item['borrower'],'')

                return make_response(jsonify({'success': 'Borrow success'}), 200)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)


