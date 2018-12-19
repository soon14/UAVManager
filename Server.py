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

import UAVManagerRoute,UAVDeviceRoute,UAVBatteryRoute,UAVFaultRoute,UAVApporvalRoute,UAVPartsRoute,UAVPlanRoute,UAVVideoRoute
import UAVPadRoute,UAVFaultReportRoute,PhotoUpload,PowerLinesRoute,UserManagerRoute,DefectRoute,DataServiceRoute
import UAVManagerDAO
import datetime

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
            #add user login log info
            logDao = UAVManagerDAO.UserLogDAO()
            logTime = datetime.datetime.now()
            department = user.user_department
            logname = username
            logDao.addUserLog(logname,department,logTime)

            rst = make_response(jsonify({'Status':True,'Token': generate_auth_token(user.user_id,3600),'ID': user.user_id,'Authority':user.user_role}))
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
api.add_resource(UserManagerRoute.UserGetID,'/usermanager/api/v1.0/user/id')
api.add_resource(UserManagerRoute.DelUserID,'/usermanager/api/v1.0/user/del/id')
api.add_resource(UserManagerRoute.UserPages,'/usermanager/api/v1.0/user/pages')
api.add_resource(UserManagerRoute.UserAdd,'/usermanager/api/v1.0/user/add')
api.add_resource(UserManagerRoute.UserModify,'/usermanager/api/v1.0/user/modify')
api.add_resource(UserManagerRoute.UserRole,'/usermanager/api/v1.0/user/role')
api.add_resource(UserManagerRoute.UserDepartment,'/usermanager/api/v1.0/user/department')
api.add_resource(UserManagerRoute.UserTeam,'/usermanager/api/v1.0/user/team')
api.add_resource(UserManagerRoute.UserTeams,'/usermanager/api/v1.0/user/teams')
#get user team manager
api.add_resource(UserManagerRoute.TeamManager,'/usermanager/api/v1.0/user/teammanager')
api.add_resource(UserManagerRoute.TeamUsers,'/usermanager/api/v1.0/team/user')
api.add_resource(UserManagerRoute.UserLogStatistic,'/usermanager/api/v1.0/logstatistic')
#api.add_resource(UserManagerRoute.AuthorityAdd,'/usermanager/api/v1.0/user/AddAuthority')


##########################################无人机管理模块
#manager related api
api.add_resource(UAVManagerRoute.ManagerListPages,'/uavmanager/api/v1.0/manager/list')
api.add_resource(UAVManagerRoute.ManagerBorrow,'/uavmanager/api/v1.0/manager/borrow')
api.add_resource(UAVManagerRoute.ManagerBorrowConfirm,'/uavmanager/api/v1.0/manager/borrow/confirm')
api.add_resource(UAVManagerRoute.ManagerReturn,'/uavmanager/api/v1.0/manager/return')
api.add_resource(UAVManagerRoute.ManagerReturnConfirm,'/uavmanager/api/v1.0/manager/return/confirm')
api.add_resource(UAVManagerRoute.ManagerListPageNum,'/uavmanager/api/v1.0/manager/pages')

api.add_resource(UAVManagerRoute.ManagerHistoryPages,'/uavmanager/api/v1.0/manager/history/list/pagenum')
api.add_resource(UAVManagerRoute.ManagerHistory,'/uavmanager/api/v1.0/manager/history/list/pages')
api.add_resource(UAVManagerRoute.ManagerHistorySearchPages,'/uavmanager/api/v1.0/manager/history/date/pagenum')
api.add_resource(UAVManagerRoute.ManagerHistorySearch,'/uavmanager/api/v1.0/manager/history/list/date')

#device related api
api.add_resource(UAVDeviceRoute.UAVDeviceList,'/uavmanager/api/v1.0/devices')
api.add_resource(UAVDeviceRoute.UAVDeviceAll,'/uavmanager/api/v1.0/devices/all')
api.add_resource(UAVDeviceRoute.UAVDeviceGetID,'/uavmanager/api/v1.0/device/id')
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
api.add_resource(UAVBatteryRoute.UAVBatteryAll,'/uavmanager/api/v1.0/batteries/all')
api.add_resource(UAVBatteryRoute.UAVBatteryGetID,'/uavmanager/api/v1.0/battery/id')
api.add_resource(UAVBatteryRoute.UAVBatteryStatisticsList,'/uavmanager/api/v1.0/battery/statistics/all')
api.add_resource(UAVBatteryRoute.UAVBatteryStatistic,'/uavmanager/api/v1.0/battery/statistic/<string:battery_status>')
api.add_resource(UAVBatteryRoute.UAVBatteryTypes,'/uavmanager/api/v1.0/battery/types')
api.add_resource(UAVBatteryRoute.UAVBatteryListPages,'/uavmanager/api/v1.0/batteries/pages')
api.add_resource(UAVBatteryRoute.UAVBatteryAdd,'/uavmanager/api/v1.0/battery/add')
api.add_resource(UAVBatteryRoute.UAVBatteryStatus,'/uavmanager/api/v1.0/battery/modify_status')
api.add_resource(UAVBatteryRoute.UAVBatteryModify,'/uavmanager/api/v1.0/battery/modify')

#parts related api
api.add_resource(UAVPartsRoute.UAVPartsList,'/uavmanager/api/v1.0/parts')
api.add_resource(UAVPartsRoute.UAVPartsAll,'/uavmanager/api/v1.0/parts/all')
api.add_resource(UAVPartsRoute.UAVPartsGetID,'/uavmanager/api/v1.0/parts/id')
api.add_resource(UAVPartsRoute.UAVPartsStatistic,'/uavmanager/api/v1.0/parts/statistic/<string:parts_status>')
api.add_resource(UAVPartsRoute.UAVPartsTypes,'/uavmanager/api/v1.0/parts/types')
api.add_resource(UAVPartsRoute.UAVPartsListPages,'/uavmanager/api/v1.0/parts/pages')
api.add_resource(UAVPartsRoute.UAVPartsAdd,'/uavmanager/api/v1.0/parts/add')
api.add_resource(UAVPartsRoute.UAVPartsStatus,'/uavmanager/api/v1.0/parts/modify_status')
api.add_resource(UAVPartsRoute.UAVPartsModify,'/uavmanager/api/v1.0/parts/modify')

#pad related api
api.add_resource(UAVPadRoute.UAVPadList,'/uavmanager/api/v1.0/pads')
api.add_resource(UAVPadRoute.UAVPadAll,'/uavmanager/api/v1.0/pads/all')
api.add_resource(UAVPadRoute.UAVPadsStatistic,'/uavmanager/api/v1.0/pad/statistic/<string:pad_status>')
api.add_resource(UAVPadRoute.UAVPadGetID,'/uavmanager/api/v1.0/pad/id')
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
api.add_resource(UAVFaultRoute.UAVFaultFinished,'/uavmanager/api/v1.0/fault/finished')
api.add_resource(UAVFaultRoute.UAVFaultScrap,'/uavmanager/api/v1.0/fault/scrap')

#fault report api
api.add_resource(UAVFaultReportRoute.FaultReportQuery, '/uavmanager/api/v1.0/faultreport')
api.add_resource(UAVFaultReportRoute.FaultReportUpdate, '/uavmanager/api/v1.0/faultreport/update')

#approval
api.add_resource(UAVApporvalRoute.UAVApprovalList, '/uavmanager/api/v1.0/approval/list')
#我提交的申请
api.add_resource(UAVApporvalRoute.UAVApprovalListApply,'/uavmanager/api/v1.0/approval/list/apply')
#待我审批的申请
api.add_resource(UAVApporvalRoute.UAVApprovalListApprove,'/uavmanager/api/v1.0/approval/list/approve')
api.add_resource(UAVApporvalRoute.UAVApprovalAdd, '/uavmanager/api/v1.0/approval/add')
api.add_resource(UAVApporvalRoute.UAVApprovalAgree, '/uavmanager/api/v1.0/approval/agree')
api.add_resource(UAVApporvalRoute.UAVApprovalDisagree, '/uavmanager/api/v1.0/approval/disagree')


#查询巡检计划
api.add_resource(UAVPlanRoute.UAVPlanSearch,'/uavmanager/api/v1.0/plan/search')

###################################################################文件上传模块
api.add_resource(PhotoUpload.FileUpload,'/gis/api/v1.0/fileupload')
api.add_resource(PhotoUpload.FileUploadDraw,'/gis/api/v1.0/fileuploaddraw')
api.add_resource(PhotoUpload.ImageUpload,'/gis/api/v1.0/imageupload')
api.add_resource(PhotoUpload.PhotoClassifyUpload,'/gis/api/v1.0/uploadclassify')

###################################################################电力线路杆塔查询模块
api.add_resource(PowerLinesRoute.PowerLineListRoute,'/gis/api/v1.0/lines')
api.add_resource(PowerLinesRoute.PowerLineSearchFuzzy,'/gis/api/v1.0/lines/search')
api.add_resource(PowerLinesRoute.PowerLineListPages,'/gis/api/v1.0/lines/pages')
api.add_resource(PowerLinesRoute.PowerLineListPageRoute,'/gis/api/v1.0/linesList')
api.add_resource(PowerLinesRoute.PowerLineDeleteRoute,'/gis/api/v1.0/linesDelete')
api.add_resource(PowerLinesRoute.PowerLineVoltageRoute,'/gis/api/v1.0/lines/lines/voltage')
api.add_resource(PowerLinesRoute.PowerLineVoltageArrayRoute,'/gis/api/v1.0/lines/lines/voltage/array')

api.add_resource(PowerLinesRoute.PowerLineRoute,'/gis/api/v1.0/line')
api.add_resource(PowerLinesRoute.PowerLineAddRoute,'/gis/api/v1.0/line/add')
api.add_resource(PowerLinesRoute.PowerLineTypeRoute,'/gis/api/v1.0/lines/type/voltage')
api.add_resource(PowerLinesRoute.PowerLineWorkteamRoute,'/gis/api/v1.0/lines/type/workteam')

api.add_resource(PowerLinesRoute.PowerLineTowerRoute,'/gis/api/v1.0/tower')
api.add_resource(PowerLinesRoute.PowerLineTowerIDRoute,'/gis/api/v1.0/tower/id')
api.add_resource(PowerLinesRoute.PowerLineTowerPagesRoute,'/gis/api/v1.0/tower/pages')
api.add_resource(PowerLinesRoute.PowerLineTowerDeleteRoute,'/gis/api/v1.0/towerDelete')

api.add_resource(PowerLinesRoute.PowerLineTowerQueryRoute,'/gis/api/v1.0/tower/query')
api.add_resource(PowerLinesRoute.PowerLineTowerAdd,'/gis/api/v1.0/tower/add')
api.add_resource(PowerLinesRoute.PowerLineTowerUpdate,'/gis/api/v1.0/tower/update')
api.add_resource(PowerLinesRoute.PowerLineTowerUpdateLocation,'/gis/api/v1.0/tower/updatelocation')

api.add_resource(PowerLinesRoute.PowerPhotoSearch,'/gis/api/v1.0/photo/search')
api.add_resource(PowerLinesRoute.PowerPhotoIdx,'/gis/api/v1.0/photo/search/idx')

api.add_resource(PowerLinesRoute.PowerLinePhotoIdxRoute,'/gis/api/v1.0/line/photo')
api.add_resource(PowerLinesRoute.PowerTowerPhotoIdxRoute,'/gis/api/v1.0/tower/photo')
api.add_resource(PowerLinesRoute.PowerTowerPhotoDate,'/gis/api/v1.0/tower/photodate')

#搜索线路视频
api.add_resource(UAVVideoRoute.VideoSearchRoute,'/gis/api/v1.0/video/search')
api.add_resource(UAVVideoRoute.VideoTimeSearchRoute,'/gis/api/v1.0/video/time/search')
api.add_resource(UAVVideoRoute.VideoUploadPartRoute,'/gis/api/v1.0/video/upload')
api.add_resource(UAVVideoRoute.VideoUploadMergeRoute,'/gis/api/v1.0/video/success')

#搜索缺陷
api.add_resource(DefectRoute.DefectLevel, '/gis/api/v1.0/defectlevel')
api.add_resource(DefectRoute.DefectPart, '/gis/api/v1.0/defectPart')
api.add_resource(DefectRoute.DefectTowerID,'/gis/api/v1.0/searchdefect/towerid')
api.add_resource(DefectRoute.DefectLineName,'/gis/api/v1.0/searchdefect/linename')
api.add_resource(DefectRoute.DefectPhotoID,'/gis/api/v1.0/searchdefect/photoid')
api.add_resource(DefectRoute.DefectPhotoIDSearch,'/gis/api/v1.0/defectsearch')
api.add_resource(DefectRoute.DefectAdd,'/gis/api/v1.0/defectadd')


api.add_resource(DataServiceRoute.DataServiceAdd, '/gis/api/v1.0/dataservice/add')
api.add_resource(DataServiceRoute.DataServiceModify,'/gis/api/v1.0/dataservice/modify')
api.add_resource(DataServiceRoute.DataServiceDelete, '/gis/api/v1.0/dataservice/del')
api.add_resource(DataServiceRoute.DataServiceSearch, '/gis/api/v1.0/dataservice/search')
api.add_resource(DataServiceRoute.DataServiceSearchLine,'/gis/api/v1.0/dataservice/search/lines')
if __name__ == '__main__':
    app.run()