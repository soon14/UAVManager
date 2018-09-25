#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
desc:此文件为数据操作接口，主要是对线路，杆塔，缺陷以及线路服务信息进行管理
     采用的SQL中间件为为SQLAlchemy；

     错误代码的定义：
     1.成功返回000001
     2.所有用户表错误代码以01XXXXXX开始 第3/4位标识类名 第5/6位标识函数名 第6/7位标识函数中的返回值
     3.所有无人机表错误代码以02XXXXXX开始 第3/4位标识类名 第5/6位标识函数名 第6/7位标识函数中的返回值
     4.所有杆塔表错误代码以03XXXXXX开始 第3/4位标识类名 第5/6位标识函数名 第6/7位标识函数中的返回值


compiler:python2.7.x

created by  : Frank.Wu
company     : GEDI
created time: 2018.08.16
version     : version 1.0.0.0
"""

import sys
import math

reload(sys)
sys.setdefaultencoding('utf8')

import ConfigParser
import json
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker,query
from UAVManagerEntity import User, Lines, Towers,Photo,DefectLevel,DefectPart,Defect,DataService, class_to_dict
from UAVManagerDAO import UserDAO
from datetime import datetime

cf = ConfigParser.ConfigParser()
cf.read("config.conf")
power_host = cf.get("power_account", "db_host")
power_port = cf.getint("power_account", "db_port")
power_user = cf.get("power_account", "db_user")
power_pass = cf.get("power_account", "db_pass")
power_name = cf.get("power_account","db_name")

secret_key = cf.get('token','SECRET_KEY')

engine_power = create_engine('mysql+mysqldb://' + power_user + ':' + power_pass + '@' + power_host + ':' + str(power_port) + '/' + power_name+'?charset=utf8',pool_size=100,pool_recycle=3600)
Session_Power= sessionmaker(bind=engine_power)

### 线路台账数据操作类
#   定义并实现线路数据增、改、删、查等操作，实现统计以及
#   author :Wu Wei
#   version:1.0.0.0
#   所有错误代码以0301XXXX开头
class LinesDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #查询线路信息（查询所有线路信息）
    def query_lines(self):
        rs = self.session_power.query(Lines).filter(Lines.deleted==0).all()
        return class_to_dict(rs)
    
    #根据线路ID查询线路信息
    #param lineID:线路ID
    def query_line(self,lineID):
        rs = self.session_power.query(Lines).filter(Lines.lines_id==lineID,Lines.deleted==0).all()
        return class_to_dict(rs)

    #根据线路名称进行模糊查询
    #param linename:线路名称
    def query_line_fuzzy(self,linename):
        filter= '%'+linename+'%'
        rs = self.session_power.query(Lines).filter(Lines.lines_name.like(filter)).all()
        return class_to_dict(rs)

    #线路进行分页查询
    #param work_team:线路班组
    #param page_size:每页显示的数据条数
    #param page_index:显示当前页
    def query_line_pages(self,work_team,page_size,page_index):
        q = self.session_power.query(Lines)
        if work_team:
            q = q.filter(Lines.lines_work_team == work_team)
        lines=q.filter(Lines.deleted==0).limit(page_size).offset((page_index - 1) * page_size).all()
        return class_to_dict(lines)

    #根据线路id删除线路
    #param user:当前登录的用户
    #param lineid:线路id
    def query_line_delete(self,user,lineid):
        line = self.session_power.query(Lines.lines_id==lineid).first()
        line.deleted=1
        try:
            self.session_power.commit()
        except:
            self.session_power.rollback()

        towers = self.session_power.query(Towers.tower_linename==line.lines_name).all()
        for tower in towers:
            try:
                self.session_power.commit()
            except:
                self.session_power.rollback()
        return 1

    #线路信息条件查询
    #param user:当前登录用户
    #param voltage:电压等级
    #param work_team:负责班组
    #param line_name:线路名称
    #param page_size:每一页显示数据的条数
    #param page_index:当前页的页码
    def query_line_condition(self,user,voltage,work_team,line_name,page_size,page_index):
        q = self.session_power.query(Lines)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if voltage:
            q = q.filter(Lines.lines_voltage==voltage)
        if work_team:
            q = q.filter(Lines.lines_work_team == work_team)
        if line_name:
            q = q.filter(Lines.lines_name == line_name)
        lines = q.filter(Lines.deleted==0).all()
        linenames=[]
        for line in lines:
            linenames.append(line.lines_name)
        if len(linenames)>0:
            towers=self.session_power.query(Towers).filter(Towers.tower_linename.in_(linenames)).limit(page_size).offset((page_index-1)*page_size).all()
            return  class_to_dict(towers)
        else:
            return None

    #条件查询杆塔页数
    #param user:当前登录用户
    #param voltage:电压等级
    #param work_team:运维班组
    #param line_name:线路名称
    #param page_size：每页展示数据条数
    def query_tower_pages(self,user,voltage,work_team,line_name,page_size):
        q = self.session_power.query(Lines)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if voltage:
            q = q.filter(Lines.lines_voltage==voltage)
        if work_team:
            q = q.filter(Lines.lines_work_team == work_team)
        if line_name:
            q = q.filter(Lines.lines_name == line_name)
        lines = q.filter(Lines.deleted==0).all()
        linenames = []
        for line in lines:
            linenames.append(line.lines_name)
        towersNum=self.session_power.query(Towers).filter(Towers.tower_linename.in_(linenames)).count()/page_size+1
        item = {}
        item['pages'] = towersNum
        return  item

    #查询分页数
    #param user:当前登录用户
    #param work_team:运维班组
    #param page_size:每页展示数据条数
    def query_line_pagesNumber(self,user,work_team,page_size):
        q = self.session_power.query(Lines)
        if work_team is not None:
            q = q.filter(Lines.lines_work_team == work_team)
        page_line=q.filter(Lines.deleted==0).count()/page_size+1
        item = {}
        item['pages'] = page_line
        return  item

    #查询线路类型
    def query_lineTypes(self):
        sql = 'select lines_voltage from tb_lines group by lines_voltage;'
        rs = self.session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['voltage'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #根据线路名称模糊查询电压等级
    #param linename:模糊查询的线路名称
    def query_lineTypesBlur(self,linename):
        sql = 'select lines_voltage from tb_lines where lines_name like \'%'+linename+'%\' group by lines_voltage;'
        rs = self.session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['voltage'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #查询线路的运维班组
    def query_lineWorkTeam(self):
        sql = 'select lines_work_team from tb_lines group by lines_work_team;'
        rs = self.session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['work_team'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #根据电压等级查询线路
    #param voltage:电压等级
    def query_lineVoltage(self,voltage):
        rs = self.session_power.query(Lines).filter(Lines.lines_voltage==voltage).all()
        return class_to_dict(rs)

    #根据电压等级和线路名称模糊查询电压等级
    #param voltage:电压等级
    #param linename:模糊查询的线路名称
    def query_lineVoltageBlur(self,voltage,linename):
        rs = self.session_power.query(Lines).filter(Lines.lines_voltage==voltage,Lines.lines_name.like('%'+linename+'%')).all()
        return class_to_dict(rs)

    #添加线路
    #param user:当前登录用户
    #param line:待添加的线路
    def add_line(self,user,line):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            self.session_power.add(line)
            try:
                self.session_power.commit()
            except:
                self.session_power.rollback()
            return 1
        else:
            return 3010901

    #添加多条线路
    #param user:当前登录的用户信息
    #param lines:待添加的多条线路
    def add_lines(self,user,lines):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            for item in lines:
                self.session_power.add(item)
                try:
                    self.session_power.commit()
                except:
                    self.session_power.rollback()
                return 1
        else:
            return 3011001

#杆塔数据处理
#包括杆塔信息的查询，修改添加等处理
#author Wu Wei
#version 1.0.0.0
#   所有错误代码以0302XXXX开头
class TowerDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #查询所有杆塔信息，无条件查询
    def query_towers_all(self):
        rs = self.session_power.query(Towers).filter(Towers.deleted==0).all()
        return class_to_dict(rs)

    #根据杆塔id查询杆塔信息
    #param tower_id:输入的杆塔id
    def query_tower_id(self,tower_id):
        rs = self.session_power.query(Towers).filter(Towers.tower_id==tower_id,Towers.deleted==0).all()
        return class_to_dict(rs)

    #查询线路下所有杆塔信息
    #param linename:线路名称
    def query_towers(self,linename):
        if linename is not None:
            rs = self.session_power.query(Towers).filter(Towers.tower_linename==linename,Towers.deleted==0).order_by(Towers.tower_idx).all()
            return class_to_dict(rs)
        else:
            return self.query_towers_all()

    #添加杆塔
    #param user:当前登录的用户信息
    #param tower:待添加的杆塔信息
    def add_tower(self,user,tower):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            self.session_power.add(tower)
            try:
                self.session_power.commit()
            except:
                self.session_power.rollback()
            return 1
        else:
            return 3020401

    #更新杆塔信息
    #param user:当前登录的用户信息
    #param tower:待添加的杆塔信息
    def update_tower(self,user,tower):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            self.session_power.merge(tower)
            try:
                self.session_power.commit()
            except:
                self.session_power.rollback()
            return 1
        else:
            return 3020501

    #添加多个杆塔
    #param user:当前登录的用户信息
    #param towers:待添加的杆塔信息
    def add_towers(self,user,towers):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            for item in towers:
                self.session_power.add(item)
                try:
                    self.session_power.commit()
                except:
                    self.session_power.rollback()
                return 1
        else:
            return 3020601

    #删除杆塔信息
    #param user:当前登录的用户
    #param towersid:待删除的杆塔id
    def del_tower(self,user,towersid):
        tower=self.session_power.query(Towers).filter(Towers.tower_id==towersid).first()
        tower.deleted=1
        try:
            self.session_power.commit()
        except:
            self.session_power.rollback()
        return 1


#杆塔数据处理
#包括杆塔信息的查询，修改添加等处理
#author Wu Wei
#version 1.0.0.0
#   所有错误代码以0303XXXX开头
class PhotoDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #查询所有照片信息（无条件查询）
    def query_photos(self):
        rs = self.session_power.query(Photo).all()
        return class_to_dict(rs)

    #查询所有杆塔下的照片
    #param towerIdx:杆塔id
    def query_photos_towerid(self,towerIdx):
        rs = self.session_power.query(Photo).filter(Photo.photo_tower_id==towerIdx).all()
        return class_to_dict(rs)

    #根据上传时间和杆塔id查询照片信息
    #param toweridx: 输入杆塔id
    #param photoDate:照片上传日期
    def query_photos_time(self,towerIdx,photoDate):
        rs = self.session_power.query(Photo).filter(Photo.photo_tower_id==towerIdx,Photo.photo_date==photoDate).all()
        return class_to_dict(rs)

    #杆塔照片的条件查询
    #param start_date:起始时间
    #param end_date:结束时间
    #param tower_id:杆塔id
    def query_photo_condition(self,start_date,end_date,tower_id):
        q=self.session_power.query(Photo)
        if start_date!=None:
            q=q.filter(Photo.photo_date>=start_date)
        if end_date != None:
            q=q.filter(Photo.photo_date<=end_date)
        if tower_id != None:
            q=q.filter(Photo.photo_tower_id==tower_id)
        photos = q.all()
        return class_to_dict(photos)

    #查询杆塔所有照片的日期信息
    #param towerid:杆塔id
    #返回日期分组
    def query_photo_date(self,towerid):
        sql = 'select photo_date from tb_photo  where photo_tower_id='+str(towerid)+' group by photo_date ;'
        rs = self.session_power.execute(sql).fetchall()
        self.session_power.rollback()
        ret = []
        for i in rs:
            item = {}
            item['date'] = i[0].strftime("%Y-%m-%d")
            ret.append(item)
        return json.dumps(ret)

    #根据照片id查询杆塔照片
    #param photoidx:输入杆塔照片id
    #返回照片信息
    def query_photo_idx(self,photoidx):
        rs = self.session_power.query(Photo).filter(Photo.photo_id == photoidx).first()
        #根据查到的线路id获取电压等级
        lineinfo = self.session_power.query(Lines).filter(Lines.lines_id==rs.photo_line).first()
        dic = class_to_dict(rs)
        dic['voltage'] = lineinfo.lines_voltage
        return dic

    #添加杆塔照片
    #param user:输入用户信息
    #param photo:输入待添加的照片信息
    def add_photo(self,user,photo):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            self.session_power.add(photo)
            try:
                self.session_power.commit()
            except:
                self.session_power.rollback()
            return 1
        else:
            return 3030701

    #添加杆塔照片
    #param voltage:输入电压等级
    #param line_id:输入线路id
    #param tower_id:输入杆塔id
    #param classify:输入照片类别
    #param path:照片存储路径（网络路径）
    #param paththumbnail:照片缩略图网络路径
    #param date:照片上传日期
    def add_photo(self, voltage, line_id, tower_id, classify, path, paththumbnail, date):
        #是否进行判断
        line = self.session_power.query(Lines).filter(Lines.lines_id==line_id).first()
        photo = Photo(photo_line=line_id,photo_tower_id=tower_id,photo_path=path,photo_thumbnail_path=paththumbnail,photo_classify=classify,photo_date=date)
        self.session_power.add(photo)
        try:
            self.session_power.commit()
        except:
            self.session_power.rollback()
        return 1

    #添加多张照片
    #param user:用户列表
    #param photos:照片信息
    def add_photos(self,user,photos):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            for item in photos:
                self.session_power.add(item)
                try:
                    self.session_power.commit()
                except:
                    self.session_power.rollback()
                return 1
        else:
            return 3030901

#缺陷等级处理，简单的进行缺陷等级的查询
#   所有错误代码以0304XXXX开头
class DefectLevelDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()
    #查询故障等级
    #param user:输入用户信息
    def query_defect_level(self,user):
        defectLevels = self.session_power.query(DefectLevel).all()
        self.session_power.rollback()
        return class_to_dict(defectLevels)

#缺陷部位查询，简单的对缺陷部位进行查询
#   所有错误代码以0305XXXX开头
class DefectPartDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #查询所有缺陷部位
    #param  user:当前登录的用户信息
    def query_defect_part(self,user):
        defectParts= self.session_power.query(DefectPart).all()
        self.session_power.rollback()
        return class_to_dict(defectParts)

#缺陷处理，缺陷的添加，缺陷查询等操作
#   所有错误代码以0305XXXX开头
class DefectDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #查询杆塔对应的缺陷的照片
    #param user:输入用户信息
    #param tower_id:用户id
    def query_defect_tower(self,user,tower_id):
        defects = self.session_power.query(Defect).filter(Defect.tb_defect_towerid==tower_id).all()
        self.session_power.rollback()
        photoids=[]
        for defect in defects:
            photoids.append(defect.tb_defect_photoid)

        photo = self.session_power.query(Photo).filter(Photo.photo_id.in_(photoids)).all()
        self.session_power.rollback()
        return class_to_dict(photo)

    #查询线路每一级杆塔对应的缺陷的数目
    #param user:输入的用户信息
    #param line_name:线路名称
    #param st_time:起始时间
    #param end_time:结束时间
    def query_defect_linename(self,user,line_name,st_time,end_time):
        #查询线路所有杆塔
        queryFunc  = self.session_power.query(func.count(Defect.tb_defect_id))
        towers = self.session_power.query(Towers).filter(Towers.tower_linename==line_name).all()
        lineids=[]
        labels=[]
        for toweritem in towers:
            queryFunc=queryFunc.filter(Defect.tb_defect_towerid==toweritem.tower_id)
            if st_time != None:
                queryFunc=queryFunc.filter(Defect.tb_defect_date>st_time)
            if end_time != None:
                queryFunc=queryFunc.filter(Defect.tb_defect_date<end_time)
            num = queryFunc.scalar()
            item['tower_lng']=toweritem.tower_lng
            item['tower_lat'] = toweritem.tower_lat
            item['tower_elevation'] = toweritem.tower_elevation
            item['tower_linename'] = toweritem.tower_linename
            item['tower_idx'] = toweritem.tower_idx
            item['number'] = num
            labels.append(item)

        """在故障中添加时间字段避免大量的查询过程
        towers = self.session_power.query(Towers).filter(Towers.tower_linename==line_name).all()
        qphoto= self.session_power.query(Photo.photo_id)
        if st_time != None:
            qphoto=qphoto.filter(Photo.photo_date>st_time)
        if end_time != None:
            qphoto=qphoto.filter(Photo.photo_date<end_time)
        photos = qphoto.all()
        photoids = []
        for itemphoto in photos:
            photoids.append(itemphoto[0])
    
        lineids=[]
        labels=[]
        for toweritem in towers:
            item={}
            num=self.session_power.query(func.count(Defect.tb_defect_id)).filter(Defect.tb_defect_towerid==toweritem.tower_id,Defect.tb_defect_photoid.in_(photoids)).scalar()
            item['tower_lng']=toweritem.tower_lng
            item['tower_lat'] = toweritem.tower_lat
            item['tower_elevation'] = toweritem.tower_elevation
            item['tower_linename'] = toweritem.tower_linename
            item['tower_idx'] = toweritem.tower_idx
            item['number'] = num
            labels.append(item)
        return labels
        """
    
    #根据电压等级和起止时间查询
    #param user:输入的用户信息
    #param voltage:电压等级
    #param st_time:起始时间
    #param end_time:结束时间
    def query_defect_line_voltage(self,user,voltage,st_time,end_time):
        #查询线路所有杆塔
        lines  = self.session_power.query(Lines.lines_name).filter(Lines.lines_voltage==voltage).all()
        towers = self.session_power.query(Towers).filter(Towers.tower_linename.in_(lines)).all()
        photos = self.session_power.query(Photo.id).filter(Photo.photo_date<end_time,Photo.photo_date>st_time).all()
        lineids=[]
        labels=[]
        for toweritem in towers:
            item={}
            num=self.session_power.query(func.count(Defect.tb_defect_id)).filter(Defect.tb_defect_towerid==toweritem.tower_id,Defect.tb_defect_photoid.in_(photos)).scalar()
            item['tower_lng']=toweritem.tower_lng
            item['tower_lat'] = toweritem.tower_lat
            item['tower_elevation'] = toweritem.tower_elevation
            item['tower_linename'] = toweritem.tower_linename
            item['tower_idx'] = toweritem.tower_idx
            item['number'] = num
            labels.append(item)
        return labels

    #根据杆塔id和照片id查询对应的照片实际上有照片id了就不太需要杆塔id了 有点鸡肋
    def query_search(self,tower_id,photo_id):
        defects = self.session_power.query(Defect).filter(Defect.tb_defect_towerid==tower_id,Defect.tb_defect_photoid==photo_id).all()
        self.session_power.rollback()
        photoids=[]
        for defect in defects:
            photoids.append(defect.tb_defect_photoid)

        photo = self.session_power.query(Photo).filter(Photo.photo_id.in_(photoids)).all()
        self.session_power.rollback()
        return class_to_dict(photo)

    #根据照片id查询缺陷
    def query_defect_photo(self,user,photo_id):
        defects = self.session_power.query(Defect).filter(Defect.tb_defect_photoid==photo_id).all()
        self.session_power.rollback()
        #photoids=[]
        #for defect in defects:
        #    photoids.append(defect.tb_defect_photoid)

        #photo = self.session_power.query(Photo).filter(Photo.photo_id.in_(photoids)).all()
        #self.session_power.rollback()
        return class_to_dict(defects)

    #添加缺陷
    def defect_add(self,defect):
        #根据照片id查询时间，根据时间然后添加到缺陷信息中
        photo_item=self.session_power.query(Photo).filter(Photo.photo_id==defect.tb_defect_photoid)
        defect.tb_defect_date=photo_item.photo_date
        self.session_power.add(defect)
        isAdd = False
        self.session_power.commit()
        return 1

#数据服务管理，用来进行数据服务查询，数据服务加载等操作
#数据服务查询模块应该独立出来单独作为一个模块
#   所有错误代码以0306XXXX开头
class DataServiceDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #添加数据服务
    #param dataservice:待添加的数据服务
    def dataservice_add(self,dataservice):
        self.session_power.add(dataservice)
        self.session_power.commit()
        return 1

    #删除数据服务
    #param dataserviceid:待删除的数据服务的id
    def dataservice_delete(self,dataserviceid):
        self.session_power.query(DataService).filter(DataService.tb_dataservice_id==dataserviceid).delete()
        self.session_power.commit()
        return 1

    #查询线路下所有数据服务
    #param linename:输入线路名称
    def dataservice_search(self,linename):
        rs=self.session_power.query(DataService).filter(DataService.tb_dataservice_linename==linename).all()
        return class_to_dict(rs)

    #查询添加了服务的线路
    def dataservice_searchLine(self):
        sql = 'select tb_dataservice_linename from tb_dataservice group by tb_dataservice_linename'
        nameList = self.session_power.execute(sql)
        rs=[]
        for item in nameList:
            tmp={}
            tmp['name']=item[0]
            rs.append(tmp)
        return rs

    #修改线路服务
    #param service_id:线路服务的id
    #param service_linename:服务的线路名称
    #param service_url:线路服务的url
    #param service_type:线路服务的类型
    def dataservice_modify(self,service_id,service_linename,service_url,service_type):
        service = self.session_power.query(DataService).filter(DataService.tb_dataservice_id==service_id).first()
        service.tb_dataservice_linename=service_linename
        service.tb_dataservice_url = service_url
        service.tb_dataservice_type=service_type
        self.session_power.commit()
        return 1
