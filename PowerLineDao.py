#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import math

reload(sys)
sys.setdefaultencoding('utf8')

import ConfigParser
import json
from sqlalchemy import create_engine
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
#

class LinesDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    def query_lines(self):
        rs = self.session_power.query(Lines).filter(Lines.deleted==0).all()
        return class_to_dict(rs)

    def query_line(self,lineID):
        rs = self.session_power.query(Lines).filter(Lines.lines_id==lineID,Lines.deleted==0).all()
        return class_to_dict(rs)

    def query_line_fuzzy(self,linename):
        filter= '%'+linename+'%'
        rs = self.session_power.query(Lines).filter(Lines.lines_name.like(filter)).all()
        return class_to_dict(rs)

    def query_line_pages(self,work_team,page_size,page_index):
        q = self.session_power.query(Lines)
        if work_team:
            q = q.filter(Lines.lines_work_team == work_team)
        lines=q.filter(Lines.deleted==0).limit(page_size).offset((page_index - 1) * page_size).all()
        return class_to_dict(lines)

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

    def query_line_pagesNumber(self,user,work_team,page_size):
        q = self.session_power.query(Lines)
        if work_team is not None:
            q = q.filter(Lines.lines_work_team == work_team)
        page_line=q.filter(Lines.deleted==0).count()/page_size+1
        item = {}
        item['pages'] = page_line
        return  item

    def query_lineTypes(self):
        sql = 'select lines_voltage from tb_lines group by lines_voltage;'
        rs = self.session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['voltage'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_lineWorkTeam(self):
        sql = 'select lines_work_team from tb_lines group by lines_work_team;'
        rs = self.session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['work_team'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_lineVoltage(self,voltage):
        rs = self.session_power.query(Lines).filter(Lines.lines_voltage==voltage).all()
        return class_to_dict(rs)

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
            return -1

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
            return -1

class TowerDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    def query_towers_all(self):
        rs = self.session_power.query(Towers).filter(Towers.deleted==0).all()
        return class_to_dict(rs)

    def query_tower_id(self,tower_id):
        rs = self.session_power.query(Towers).filter(Towers.tower_id==tower_id,Towers.deleted==0).all()
        return class_to_dict(rs)

    def query_towers(self,linename):
        if linename is not None:
            rs = self.session_power.query(Towers).filter(Towers.tower_linename==linename,Towers.deleted==0).order_by(Towers.tower_idx).all()
            return class_to_dict(rs)
        else:
            return self.query_towers_all()

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
            return -1

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
            return -1

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
            return -1

    def del_tower(self,user,towersid):
        tower=self.session_power.query(Towers).filter(Towers.tower_id==towersid).first()
        tower.deleted=1
        try:
            self.session_power.commit()
        except:
            self.session_power.rollback()
        return 1

class PhotoDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    def query_photos(self):
        rs = self.session_power.query(Photo).all()
        return class_to_dict(rs)

    def query_photos_towerid(self,towerIdx):
        rs = self.session_power.query(Photo).filter(Photo.photo_tower_id==towerIdx).all()
        return class_to_dict(rs)

    def query_photos_time(self,towerIdx,photoDate):
        rs = self.session_power.query(Photo).filter(Photo.photo_tower_id==towerIdx,Photo.photo_date==photoDate).all()
        return class_to_dict(rs)

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

    def query_photo_idx(self,photoidx):
        rs = self.session_power.query(Photo).filter(Photo.photo_id == photoidx).first()
        #根据查到的线路id获取电压等级
        lineinfo = self.session_power.query(Lines).filter(Lines.lines_id==rs.photo_line).first()
        dic = class_to_dict(rs)
        dic['voltage'] = lineinfo.lines_voltage
        return dic

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
            return -1

    def add_photo(self,voltage,line_id,tower_id,classify,path,paththumbnail,date):
        #是否进行判断
        line = self.session_power.query(Lines).filter(Lines.lines_id==line_id).first()
        photo = Photo(photo_line=line_id,photo_tower_id=tower_id,photo_path=path,photo_thumbnail_path=paththumbnail,photo_classify=classify,photo_date=date)
        self.session_power.add(photo)
        try:
            self.session_power.commit()
        except:
            self.session_power.rollback()
        return 1

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
            return -1

class DefectLevelDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    def query_defect_level(self,user):
        defectLevels = self.session_power.query(DefectLevel).all()
        self.session_power.rollback()
        return class_to_dict(defectLevels)

class DefectPartDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    def query_defect_part(self,user):
        defectParts= self.session_power.query(DefectPart).all()
        self.session_power.rollback()
        return class_to_dict(defectParts)

class DefectDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    #查询杆塔对应的缺陷的照片
    def query_defect_tower(self,user,tower_id):
        defects = self.session_power.query(Defect).filter(Defect.tb_defect_towerid==tower_id).all()
        self.session_power.rollback()
        photoids=[]
        for defect in defects:
            photoids.append(defect.tb_defect_photoid)

        photo = self.session_power.query(Photo).filter(Photo.photo_id.in_(photoids)).all()
        self.session_power.rollback()
        return class_to_dict(photo)

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
        self.session_power.add(defect)
        isAdd = False
        self.session_power.commit()
        return 1
        ###
        #try:
        #    self.session_power.commit()
        #    isAdd = True
        #except:
        #    self.session_power.rollback()
        #    isAdd = False
        #if isAdd:
        #    return 1
        #else:
        #    return -1

class DataServiceDao:
    def __init__(self):
        self.session_power= Session_Power()
    def __del__(self):
        self.session_power.close()

    def dataservice_add(self,dataservice):
        self.session_power.add(dataservice)
        self.session_power.commit()
        return 1

    def dataservice_delete(self,dataserviceid):
        self.session_power.query(DataService).filter(DataService.tb_dataservice_id==dataserviceid).delete()
        self.session_power.commit()
        return 1

    def dataservice_search(self,linename):
        rs=self.session_power.query(DataService).filter(DataService.tb_dataservice_linename==linename).all()
        return class_to_dict(rs)

    def dataservice_searchLine(self):
        sql = 'select tb_dataservice_linename from tb_dataservice group by tb_dataservice_linename'
        nameList = self.session_power.execute(sql)
        rs=[]
        for item in nameList:
            tmp={}
            tmp['name']=item[0]
            rs.append(tmp)
        return rs

