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
from PowerLineDao import LinesDao, TowerDao,PhotoDao
from UAVManagerDAO import UserDAO
from UAVManagerEntity import User,Lines,Towers
parser = reqparse.RequestParser()
parser.add_argument('linename', type=str, location='args')
parser.add_argument('lineid', type=int, location='args')
parser.add_argument('towerid', type=int, location='args')
parser.add_argument('voltage', type=str, location='args')
parser.add_argument('work_team', type=str, location='args')
parser.add_argument('line_name', type=str, location='args')
parser.add_argument('page_size', type=int, location='args')
parser.add_argument('page_index', type=int, location='args')

class PowerLineListRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_lines()
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()

        lineid = args.get('lineid')
        rs=self.dao.query_line(lineid)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return json.dumps(rs)
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineListPageRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        work_team=args.get('work_team')
        page_size = args.get('page_size')
        page_index = args.get('page_index')
        rs=self.dao.query_line_pages(work_team,page_size,page_index)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineDeleteRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            lineid=args.get('lineid')
            rs=self.dao.query_line_delete(user,lineid)
            if rs!=1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


class PowerLineTypeRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_lineTypes()
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineWorkteamRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        rs=self.dao.query_lineWorkTeam()
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineVoltageRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        #if (request.data != ""):
        #    data = json.loads(request.data)
        #    token = data['token']
        #    user = self.userDao.verify_token(token, '')
        #    if (not user):
        #         return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        voltage = args.get('voltage')
        rs=self.dao.query_lineVoltage(voltage)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineAddRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
             data = json.loads(request.data)
             token = data['token']
             lineInfo = data['line']
             user = self.userDao.verify_token(token, '')
             if (not user):
                  return make_response(jsonify({'error': 'Unauthorized access'}), 401)
             line=Lines()
             line.lines_name=lineInfo[0]['lines_name']
             line.lines_construct_date = lineInfo[0]['lines_construct_date']
             line.lines_voltage = lineInfo[0]['lines_voltage']
             line.lines_work_team = lineInfo[0]['lines_work_team']
             line.lines_incharge = lineInfo[0]['lines_incharge']
             rs=self.dao.add_line(user,line)
             if rs==-1:
                  return make_response(jsonify({'error': 'Unauthorized access'}), 401)
             else:
                  return make_response(jsonify({'success': 'add data access'}), 401)
        return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()   

class PowerLineListPages(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
             data = json.loads(request.data)
             token = data['token']
             args = parser.parse_args()
             page_size = args.get('page_size')
             user = self.userDao.verify_token(token, '')
             if (not user):
                  return make_response(jsonify({'error': 'Unauthorized access'}), 401)
             rs=self.dao.query_line_pagesNumber(user,page_size)
             if rs==None:
                  return make_response(jsonify({'error': 'Unauthorized access'}), 401)
             else:
                  return rs
        return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

##################################################
class PowerLineTowerQueryRoute(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            voltage = args.get('voltage')
            work_team = args.get('work_team')
            line_name = args.get('line_name')
            page_size = args.get('page_size')
            page_index = args.get('page_index')
            rs = self.dao.query_line_condition(user,voltage,work_team,line_name,page_size,page_index)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineTowerRoute(Resource):
    def __init__(self):
        self.dao = TowerDao()
        self.userDao = UserDAO()

    def post(self):
        # if (request.data != ""):
        #     data = json.loads(request.data)
        #     token = data['token']
        #     user = self.userDao.verify_token(token, '')
        #     if (not user):
        #          return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        linename = args.get('linename')
        rs=self.dao.query_towers(linename)
        if rs==None:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
            return rs
        #     else:
        #         return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineTowerAdd(Resource):
    def __init__(self):
        self.dao = TowerDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            towerdict = data['tower']
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            tower=Towers()
            tower.tower_linename=towerdict[0]['tower_linename']
            tower.tower_idx=towerdict[0]['tower_idx']
            tower.tower_type=towerdict[0]['tower_type']
            tower.tower_height=towerdict[0]['tower_height']
            tower.tower_lat=towerdict[0]['tower_lat']
            tower.tower_lng=towerdict[0]['tower_lng']
            tower.tower_elevation=towerdict[0]['tower_elevation']
            rs = self.dao.add_tower(user,tower)
            if rs==-1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return make_response(jsonify({'success': 'Add data success'}), 401)
        else:
             return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

class PowerLineTowerDeleteRoute(Resource):
    def __init__(self):
        self.dao = TowerDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            user = self.userDao.verify_token(token, '')
            if (not user):
                 return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            args = parser.parse_args()
            towerid=args.get('lineid')
            rs=self.dao.del_tower(user,towerid)
            if rs!=1:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()


class PowerLineTowerPagesRoute(Resource):
    def __init__(self):
        self.dao = TowerDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            token = data['token']
            args = parser.parse_args()
            voltage = args.get('voltage')
            work_team = args.get('work_team')
            line_name = args.get('line_name')
            page_size = args.get('page_size')
            user = self.userDao.verify_token(token, '')
            if (not user):
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            lineDao = LinesDao()
            rs = lineDao.query_tower_pages(user,voltage,work_team,line_name,page_size)
            if rs==None:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
            else:
                return rs
        else:
             return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

######################################################



class PwoerLinePhotoIdxRoute(Resource):
    def __init__(self):
        self.dao = PhotoDao()
        self.userDao = UserDAO()

    def post(self):
        # if (request.data != ""):
        #     data = json.loads(request.data)
        #     token = data['token']
        #     toweridx = data['toweridx']
        #     user = self.userDao.verify_token(token, '')
        #     if (not user):
        #          return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        args = parser.parse_args()
        lineidx = args.get('towerid')
        rs=self.dao.query_photos(lineidx)
        if rs==None:
             return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()
