#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于线路杆塔，照片以及服务数据表，并对请求进行响应，通过Flask构建服务器解析请求
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
from PowerLineDao import LinesDao, TowerDao, PhotoDao, extractTowerIdx
from UAVManagerDAO import UserDAO
from UAVManagerEntity import User,Lines,Towers
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('linename', type=str, location='args')
parser.add_argument('lineid', type=int, location='args')
parser.add_argument('towerid', type=int, location='args')
parser.add_argument('photoid', type=int, location='args')
parser.add_argument('voltage', type=str, location='args')
parser.add_argument('work_team', type=str, location='args')
parser.add_argument('line_name', type=str, location='args')
parser.add_argument('page_size', type=int, location='args')
parser.add_argument('page_index', type=int, location='args')
parser.add_argument('photo_date', type=str, location='args')
parser.add_argument('start_time', type=str, location='args')
parser.add_argument('end_time', type=str, location='args')

#查询所有线路信息url的解析与响应
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
            return make_response(jsonify({'error': '查询线路信息失败','errorcode':10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#线路信息的模糊查询的url的解析与响应
class PowerLineSearchFuzzy(Resource):
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

        linename = args.get('linename')
        rs=self.dao.query_line_fuzzy(linename)
        if rs==None:
            return make_response(jsonify({'error': '根据线路名称查询线路信息失败','errorcode':10000000}), 401)
        else:
            return json.dumps(rs)
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据线路id查询线路信息的url的解析与响应
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
            return make_response(jsonify({'error': '根据线路id查询线路信息失败','errorcode':10000000}), 401)
        else:
            return json.dumps(rs)
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#线路信息的分页与条件查询的url的解析与响应
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
            return make_response(jsonify({'error': '查询线路信息失败','errorcode':10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#删除线路信息的url的解析与响应的url的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期','errorcode':10000000}), 401)
            if user==1010301:
                return make_response(jsonify({'error': '登录过期','errorcode':user}), 401)
            if user==1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            args = parser.parse_args()
            lineid=args.get('lineid')
            rs=self.dao.query_line_delete(user,lineid)
            if rs!=1:
                return make_response(jsonify({'error': '根据线路id查询线路信息失败','error':10000000}), 401)
            else:
                return rs
        else:
            return make_response(jsonify({'error': '没有登录，无权限查询线路信息'}), 401)

    def get(self):
        return self.post()

#查询所有线路的电压等级情况的url的解析与响应
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
        args = parser.parse_args()
        linename = args.get('linename')
        rs=[]
        if(linename==None or linename==''):
            rs=self.dao.query_lineTypes()
        else:
            rs = self.dao.query_lineTypesBlur(linename)

        if rs==None:
            return make_response(jsonify({'error': '查询线路电压等级失败','errorcode':10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#查询线路的运维班组情况的url的解析与响应
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
            return make_response(jsonify({'error': '查询线路维护班组失败','errorcode':10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据电压等级查询线路信息的url的解析与响应
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
        linename= args.get('linename')
        rs=[];
        if(linename==None):
            rs=self.dao.query_lineVoltage(voltage)
        else:
            rs=self.dao.query_lineVoltageBlur(voltage,linename)
        if rs==None:
            return make_response(jsonify({'error': '根据电压等级查询线路信息失败','errorcode':10000000}), 401)
        else:
            return rs
    #else:
        #    return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据电压等级查询线路信息的url的解析与响应,传出数组
class PowerLineVoltageArrayRoute(Resource):
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
        linename= args.get('linename')
        rs=[];
        if(linename==None):
            rs=self.dao.query_lineVoltage(voltage)
        else:
            rs=self.dao.query_lineVoltageBlur(voltage,linename)
        if rs==None:
            return make_response(jsonify({'error': '根据电压等级查询线路信息失败','errorcode':10000000}), 401)
        else:
            return json.dumps(obj=rs)

    def get(self):
        return self.post()



#添加线路信息的url的解析与响应
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
                 return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
             if user == 1010301:
                 return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
             if user == 1010302:
                 return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

             line=Lines()
             line.lines_name=lineInfo[0]['lines_name']
             line.lines_construct_date = lineInfo[0]['lines_construct_date']
             line.lines_voltage = lineInfo[0]['lines_voltage']
             line.lines_work_team = lineInfo[0]['lines_work_team']
             line.lines_incharge = lineInfo[0]['lines_incharge']
             rs=self.dao.add_line(user,line)
             if rs==3010901:
                  return make_response(jsonify({'error': '没有权限添加线路'}), 401)
             else:
                  return make_response(jsonify({'success': '添加线路成功'}), 200)
        return  make_response(jsonify({'error': '传入参数错误'}), 401)

    def get(self):
        return self.post()   

#查询线路信息总页数的url的解析与响应

class PowerLineListPages(Resource):
    def __init__(self):
        self.dao = LinesDao()
        self.userDao = UserDAO()

    def post(self):
        if (request.data != ""):
             data = json.loads(request.data)
             token = data['token']
             args = parser.parse_args()
             work_team = args.get('work_team')
             page_size = args.get('page_size')
             user = self.userDao.verify_token(token, '')
             user = self.userDao.verify_token(token, '')
             if (not user):
                 return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
             if user == 1010301:
                 return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
             if user == 1010302:
                 return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

             rs=self.dao.query_line_pagesNumber(user,work_team,page_size)
             if rs==None:
                  return make_response(jsonify({'error': '查询线路分页数失败', 'errorcode': 10000000}), 401)
             else:
                  return rs
        return  make_response(jsonify({'error': '传入参数错误'}), 401)

    def get(self):
        return self.post()

##################################################
#根据条件查询分页查询杆塔信息的url的解析与响应
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
                 return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                 return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                 return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            args = parser.parse_args()
            voltage = args.get('voltage')
            work_team = args.get('work_team')
            line_name = args.get('line_name')
            page_size = args.get('page_size')
            page_index = args.get('page_index')
            rs = self.dao.query_line_condition(user,voltage,work_team,line_name,page_size,page_index)
            if rs==None:
                return make_response(jsonify({'error': '查询杆塔信息失败','errorcode':10000000}), 401)
            else:
                return rs
        else:
            return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据线路名称查询杆塔的url的解析与响应
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
            return make_response(jsonify({'error': '根据线路名称查询杆塔失败','errorcode':10000000}), 401)
        else:
            return rs
        #     else:
        #         return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据杆塔id查询杆塔的url的解析与响应
class PowerLineTowerIDRoute(Resource):
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
        tower_id = args.get('towerid')
        rs=self.dao.query_tower_id(tower_id)
        if rs==None:
            return make_response(jsonify({'error': '根据杆塔id查询杆塔信息失败','errorcode':10000000}), 401)
        else:
            return rs
        #     else:
        #         return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#添加杆塔信息的url的解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            tower=Towers()
            tower.tower_linename=towerdict[0]['tower_linename']
            tower.tower_idx=extractTowerIdx(towerdict[0]['tower_idx'])
            tower.tower_type=towerdict[0]['tower_type']
            tower.tower_height=towerdict[0]['tower_height']
            tower.tower_lat=towerdict[0]['tower_lat']
            tower.tower_lng=towerdict[0]['tower_lng']
            tower.tower_elevation=towerdict[0]['tower_elevation']
            rs = self.dao.add_tower(user,tower)
            if rs==3020401:
                return make_response(jsonify({'error': '无权限添加杆塔','errorcode':rs}), 401)
            else:
                return make_response(jsonify({'success': '添加杆塔成功'}), 200)
        else:
             return  make_response(jsonify({'error': '传入参数错误'}), 401)

    def get(self):
        return self.post()

#杆塔数据更新的url解析与响应
class PowerLineTowerUpdate(Resource):
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            tower=Towers()
            tower.tower_linename=towerdict['tower_linename']
            tower.tower_id=towerdict['tower_id']
            tower.tower_idx = extractTowerIdx(towerdict['tower_idx'])
            tower.tower_type=towerdict['tower_type']
            tower.tower_lat=towerdict['tower_lat']
            tower.tower_lng=towerdict['tower_lng']
            tower.tower_date = datetime.strptime(towerdict['tower_date'],'%Y-%m-%d').date()
            tower.tower_span_small = towerdict['tower_span_small']
            tower.tower_span_horizonal = towerdict['tower_span_horizonal']
            tower.tower_span_vertical = towerdict['tower_span_vertical']
            tower.tower_rotation_direction = towerdict['tower_rotation_direction']
            tower.tower_rotation_degree = towerdict['tower_rotation_degree']
            tower.tower_descriptor = towerdict['tower_descriptor']
            tower.tower_lightarrest_type = towerdict['tower_lightarrest_type']
            tower.tower_insulator_material = towerdict['tower_insulator_material']
            tower.tower_insulator_type = towerdict['tower_insulator_type']
            tower.tower_insulator_strand = towerdict['tower_insulator_strand']
            tower.tower_insulator_double = towerdict['tower_insulator_double']
            tower.tower_insulator_doublehang = towerdict['tower_insulator_doublehang']
            tower.tower_opgw_type = towerdict['tower_opgw_type']
            rs = self.dao.update_tower(user,tower)
            if rs==3020501:
                return make_response(jsonify({'error': '无权限更新杆塔信息','errorcode':rs}), 401)
            else:
                return make_response(jsonify({'success': '添加杆塔信息成功'}), 200)
        else:
             return  make_response(jsonify({'error': '传入参数错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#更新杆塔坐标的url的解析与响应
class PowerLineTowerUpdateLocation(Resource):
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)

            tower=Towers()
            tower.tower_id=towerdict['tower_id']
            tower.tower_lat=towerdict['tower_lat']
            tower.tower_lng=towerdict['tower_lng']
            rs = self.dao.update_tower(user,tower)
            if rs==3020501:
                return make_response(jsonify({'error': '无权限更新杆塔坐标','errorcode':rs}), 401)
            else:
                return make_response(jsonify({'success': '更新杆塔坐标成功'}), 200)
        else:
             return  make_response(jsonify({'error': '传入参数出错','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#删除杆塔的url解析与响应
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
                return make_response(jsonify({'error': '用户不存在或登录过期', 'errorcode': 10000000}), 400)
            if user == 1010301:
                return make_response(jsonify({'error': '登录过期', 'errorcode': user}), 400)
            if user == 1010302:
                return make_response(jsonify({'error': '用户验证错误', 'errorcode': user}), 400)


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

#条件查询杆塔分页查询的url解析与响应
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
#根据线路id查询杆塔照片的url解析与响应（实现的是查询所有照片）
class PowerLinePhotoIdxRoute(Resource):
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
             return make_response(jsonify({'error': '查询杆塔照片失败','errorcode':10000000}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据杆塔id与照片日期查询照片的url解析与响应
class PowerTowerPhotoIdxRoute(Resource):
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
        toweridx = args.get('towerid')
        strDate = args.get('photo_date')

        rs=None
        if strDate==None:
            rs = self.dao.query_photos_towerid(toweridx)
        else:
            photodate = datetime.strptime(strDate, '%Y-%m-%d')
            rs = self.dao.query_photos_time(toweridx,photodate)

        if rs==None:
             return make_response(jsonify({'error': '查询杆塔照片失败','errorcode':10000000}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#查询杆塔下所有照片的上传时间的请求url的解析与响应
class PowerTowerPhotoDate(Resource):
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
        toweridx = args.get('towerid')
        rs=self.dao.query_photo_date(toweridx)
        if rs==None:
             return make_response(jsonify({'error': '查询杆塔照片日期失败','errorcode':10000000}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据杆塔坐标和起止日期查询杆塔照片信息的请求url的解析与响应
class PowerPhotoSearch(Resource):
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
        toweridx = args.get('towerid')
        start_time = datetime.strptime(args.get('start_time'),'%Y-%m-%d').date()
        end_time = datetime.strptime(args.get('end_time'),'%Y-%m-%d').date()
        rs=self.dao.query_photo_condition(start_time,end_time,toweridx)
        if rs==None:
             return make_response(jsonify({'error': '查询杆塔照片失败','errorcode':10000000}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()

#根据杆塔id查询杆塔信息请求url的解析与响应
class PowerPhotoIdx(Resource):
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
        photoid = args.get('photoid')
        rs=self.dao.query_photo_idx(photoid)
        if rs==None:
             return make_response(jsonify({'error': '根据照片id查询杆塔照片失败','errorcode':10000000}), 401)
        else:
             return rs
        # else:
        #     return  make_response(jsonify({'error': 'Unauthorized access'}), 401)

    def get(self):
        return self.post()