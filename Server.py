#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import ConfigParser
import json
from flask import Flask, request ,jsonify
from flask import Response,make_response
from flask_cors import CORS
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
from flask import Flask, render_template

import UAVManagerRoute,UAVDeviceRoute,UAVBatteryRoute,UAVFaultRoute,UAVApporvalRoute,UAVPartsRoute,UAVPadRoute,UAVFaultReportRoute,PhotoUpload,PowerLinesRoute,UserManagerRoute
import UAVManagerDAO

auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)
CORS(app)
cf = ConfigParser.ConfigParser()
cf.read("config.conf")
secret_key = cf.get('token','SECRET_KEY')

def generate_auth_token(userid, expiration):
    s = Serializer(secret_key, expires_in=expiration)
    return s.dumps({'id': userid})

@auth.verify_password
def verify_password(username_or_token,password):
    userDao = UAVManagerDAO.UserDAO()
    user = userDao.verify_token(username_or_token,password)
    if(not user):
        return userDao.verify_password(username_or_token, password)
    return True

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

##########################################登录模块

@app.route('/uavmanager/api/v1.0/login', methods=['GET', 'POST'])
def login():
    if(request.data!=""):
        data=json.loads(request.data)
        username = str(data['username'])
        password = str(data['password'])

        userDao = UAVManagerDAO.UserDAO()
        user = userDao.get_user_byName(username)
        if(userDao.verify_password(username,password)):
            rst = make_response(jsonify({'Status':True,'Token': generate_auth_token(user.user_id,3600),'ID': user.user_id}))
            rst.headers['Access-Control-Allow-Origin'] = '*'
            rst.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
            rst.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        else:
            rst = make_response(jsonify({'Status': False}))
    else:
        rst = make_response(jsonify({'Status': False}))

    return rst

##########################################用户权限管理模块
api.add_resource(UserManagerRoute.UserList,'/usermanager/api/v1.0/user/list')
api.add_resource(UserManagerRoute.UserAdd,'/usermanager/api/v1.0/user/Add')
#api.add_resource(UserManagerRoute.AuthorityAdd,'/usermanager/api/v1.0/user/AddAuthority')


##########################################无人机管理模块
#manager related api
api.add_resource(UAVManagerRoute.ManagerListPages,'/uavmanager/api/v1.0/manager/list')
api.add_resource(UAVManagerRoute.ManagerBorrow,'/uavmanager/api/v1.0/manager/borrow')
api.add_resource(UAVManagerRoute.ManagerReturn,'/uavmanager/api/v1.0/manager/return')
api.add_resource(UAVManagerRoute.ManagerListPageNum,'/uavmanager/api/v1.0/manager/pages')


#device related api
api.add_resource(UAVDeviceRoute.UAVDeviceList,'/uavmanager/api/v1.0/devices')
api.add_resource(UAVDeviceRoute.UAVDeviceManagerSearch,'/uavmanager/api/v1.0/device/<int:id>')
api.add_resource(UAVDeviceRoute.UAVDeviceManagerStatisticList,'/uavmanager/api/v1.0/device/statistics/all')
api.add_resource(UAVDeviceRoute.UAVDeviceManagerStatistic,'/uavmanager/api/v1.0/device/statistic/<string:status>')
api.add_resource(UAVDeviceRoute.UAVDeviceTypes,'/uavmanager/api/v1.0/device/types')
api.add_resource(UAVDeviceRoute.UAVDeviceVers,'/uavmanager/api/v1.0/device/vers')
api.add_resource(UAVDeviceRoute.UAVDeviceListPages,'/uavmanager/api/v1.0/devices/pages')
api.add_resource(UAVDeviceRoute.UAVDeviceAdd,'/uavmanager/api/v1.0/device/add')
api.add_resource(UAVDeviceRoute.UAVDeviceStatus,'/uavmanager/api/v1.0/device/modify_status')
api.add_resource(UAVDeviceRoute.UAVDeviceModify,'/uavmanager/api/v1.0/device/modify')

#battery related api
api.add_resource(UAVBatteryRoute.UAVBatteryList,'/uavmanager/api/v1.0/batteries')
api.add_resource(UAVBatteryRoute.UAVBatteryStatisticsList,'/uavmanager/api/v1.0/battery/statistics/all')
api.add_resource(UAVBatteryRoute.UAVBatteryStatistic,'/uavmanager/api/v1.0/battery/statistic/<string:battery_status>')
api.add_resource(UAVBatteryRoute.UAVBatteryTypes,'/uavmanager/api/v1.0/battery/types')
api.add_resource(UAVBatteryRoute.UAVBatteryListPages,'/uavmanager/api/v1.0/batteries/pages')
api.add_resource(UAVBatteryRoute.UAVBatteryAdd,'/uavmanager/api/v1.0/battery/add')
api.add_resource(UAVBatteryRoute.UAVBatteryStatus,'/uavmanager/api/v1.0/battery/modify_status')
api.add_resource(UAVBatteryRoute.UAVBatteryModify,'/uavmanager/api/v1.0/battery/modify')

#parts related api
api.add_resource(UAVPartsRoute.UAVPartsList,'/uavmanager/api/v1.0/parts')
api.add_resource(UAVPartsRoute.UAVPartsStatistic,'/uavmanager/api/v1.0/parts/statistic/<string:parts_status>')
api.add_resource(UAVPartsRoute.UAVPartsTypes,'/uavmanager/api/v1.0/parts/types')
api.add_resource(UAVPartsRoute.UAVPartsListPages,'/uavmanager/api/v1.0/parts/pages')
api.add_resource(UAVPartsRoute.UAVPartsAdd,'/uavmanager/api/v1.0/parts/add')
api.add_resource(UAVPartsRoute.UAVPartsStatus,'/uavmanager/api/v1.0/parts/modify_status')
api.add_resource(UAVPartsRoute.UAVPartsModify,'/uavmanager/api/v1.0/parts/modify')

#pad related api
api.add_resource(UAVPadRoute.UAVPadList,'/uavmanager/api/v1.0/pad/list')
api.add_resource(UAVPadRoute.UAVPadListPages,'/uavmanager/api/v1.0/pad/pages')
api.add_resource(UAVPadRoute.UAVPadTypes,'/uavmanager/api/v1.0/pad/types')
api.add_resource(UAVPadRoute.UAVPadAdd,'/uavmanager/api/v1.0/pad/add')
api.add_resource(UAVPadRoute.UAVPadStatus,'/uavmanager/api/v1.0/pad/modify_status')
api.add_resource(UAVPadRoute.UAVPadModify,'/uavmanager/api/v1.0/pad/modify')

#fault related api
api.add_resource(UAVFaultRoute.UAVFaultStatistics,'/uavmanager/api/v1.0/fault/statistics')
api.add_resource(UAVFaultRoute.UAVFaultList,'/uavmanager/api/v1.0/fault/list')
api.add_resource(UAVFaultRoute.UAVFaultDeviceVersion,'/uavmanager/api/v1.0/fault/device_ver')
api.add_resource(UAVFaultRoute.UAVFaultListPages,'/uavmanager/api/v1.0/fault/pages')
api.add_resource(UAVFaultRoute.UAVFaultAdd,'/uavmanager/api/v1.0/fault/add')

#fault report api
api.add_resource(UAVFaultReportRoute.FaultReportQuery, '/uavmanager/api/v1.0/faultreport')
api.add_resource(UAVFaultReportRoute.FaultReportUpdate, '/uavmanager/api/v1.0/faultreport/update')


#approval
api.add_resource(UAVApporvalRoute.UAVApprovalList, '/uavmanager/api/v1.0/approval/list')
api.add_resource(UAVApporvalRoute.UAVApprovalAdd, '/uavmanager/api/v1.0/approval/add')
api.add_resource(UAVApporvalRoute.UAVApprovalAgree, '/uavmanager/api/v1.0/approval/agree')
api.add_resource(UAVApporvalRoute.UAVApprovalDisagree, '/uavmanager/api/v1.0/approval/disagree')

###################################################################文件上传模块
api.add_resource(PhotoUpload.FileUpload,'/gis/api/v1.0/FileUpload')
api.add_resource(PhotoUpload.ImageUpload,'/gis/api/v1.0/imageupload')

###################################################################电力线路杆塔查询模块
api.add_resource(PowerLinesRoute.PowerLineListRoute,'/gis/api/v1.0/lines')
api.add_resource(PowerLinesRoute.PowerLineListPages,'/gis/api/v1.0/lines/pages')
api.add_resource(PowerLinesRoute.PowerLineListPageRoute,'/gis/api/v1.0/linesList')
api.add_resource(PowerLinesRoute.PowerLineDeleteRoute,'/gis/api/v1.0/linesDelete')
api.add_resource(PowerLinesRoute.PowerLineVoltageRoute,'/gis/api/v1.0/lines/lines/voltage')

api.add_resource(PowerLinesRoute.PowerLineRoute,'/gis/api/v1.0/line')
api.add_resource(PowerLinesRoute.PowerLineAddRoute,'/gis/api/v1.0/line/add')
api.add_resource(PowerLinesRoute.PowerLineTypeRoute,'/gis/api/v1.0/lines/type/voltage')
api.add_resource(PowerLinesRoute.PowerLineWorkteamRoute,'/gis/api/v1.0/lines/type/workteam')

api.add_resource(PowerLinesRoute.PowerLineTowerRoute,'/gis/api/v1.0/tower')
api.add_resource(PowerLinesRoute.PowerLineTowerPagesRoute,'/gis/api/v1.0/tower/pages')
api.add_resource(PowerLinesRoute.PowerLineTowerDeleteRoute,'/gis/api/v1.0/towerDelete')

api.add_resource(PowerLinesRoute.PowerLineTowerQueryRoute,'/gis/api/v1.0/tower/query')
api.add_resource(PowerLinesRoute.PowerLineTowerAdd,'/gis/api/v1.0/tower/add')

api.add_resource(PowerLinesRoute.PwoerLinePhotoIdxRoute,'/gis/api/v1.0/photo')
#api.add_resource(PowerLinesRoute.PwoerLinePhotoIdxRoute,'/gis/api/v1.0/photozip')
#api.add_resource(PowerLinesRoute.PwoerLinePhotoTypeRoute,'/gis/api/v1.0/photo/types')


if __name__ == '__main__':
    app.run()