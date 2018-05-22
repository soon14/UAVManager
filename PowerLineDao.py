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
from UAVManagerEntity import User, Lines, Towers,Photo, class_to_dict
from UAVManagerDAO import UserDAO

cf = ConfigParser.ConfigParser()
cf.read("config.conf")
power_host = cf.get("power_account", "db_host")
power_port = cf.getint("power_account", "db_port")
power_user = cf.get("power_account", "db_user")
power_pass = cf.get("power_account", "db_pass")
power_name = cf.get("power_account","db_name")

secret_key = cf.get('token','SECRET_KEY')

engine_power = create_engine('mysql+mysqldb://' + power_user + ':' + power_pass + '@' + power_host + ':' + str(power_port) + '/' + power_name+'?charset=utf8')
Session_Power= sessionmaker(bind=engine_power)
session_power = Session_Power()

class LinesDao:
    def query_lines(self):
        rs = session_power.query(Lines).filter(Lines.deleted==0).all()
        return class_to_dict(rs)

    def query_line(self,lineID):
        rs = session_power.query(Lines).filter(Lines.lines_id==lineID,Lines.deleted==0).all()
        return class_to_dict(rs)

    def query_line_pages(self,work_team,page_size,page_index):
        q = session_power.query(Lines)
        if work_team:
            q = q.filter(Lines.lines_work_team == work_team)
        lines=q.filter(Lines.deleted==0).limit(page_size).offset((page_index - 1) * page_size).all()
        return class_to_dict(lines)

    def query_line_delete(self,user,lineid):
        line = session_power.query(Lines.lines_id==lineid).first()
        line.deleted=1
        session_power.commit()

        towers = session_power.query(Towers.tower_linename==line.lines_name).all()
        for tower in towers:
            tower.deleted=1
            session_power.commit()
        return 1

    def query_line_condition(self,user,voltage,work_team,line_name,page_size,page_index):
        q = session_power.query(Lines)
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
            towers=session_power.query(Towers).filter(Towers.tower_linename.in_(linenames)).limit(page_size).offset((page_index-1)*page_size).all()
            return  class_to_dict(towers)
        else:
            return None

    def query_tower_pages(self,user,voltage,work_team,line_name,page_size):
        q = session_power.query(Lines)
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
        towersNum=session_power.query(Towers).filter(Towers.tower_linename.in_(linenames)).count()/page_size+1
        item = {}
        item['pages'] = towersNum
        return  item

    def query_line_pagesNumber(self,user,work_team,page_size):
        q = session_power.query(Lines)
        if work_team is not None:
            q = q.filter(Lines.lines_work_team == work_team)
        page_line=q.filter(Lines.deleted==0).count()/page_size+1
        item = {}
        item['pages'] = page_line
        return  item

    def query_lineTypes(self):
        sql = 'select lines_voltage from tb_lines group by lines_voltage;'
        rs = session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['voltage'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_lineWorkTeam(self):
        sql = 'select lines_work_team from tb_lines group by lines_work_team;'
        rs = session_power.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['work_team'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_lineVoltage(self,voltage):
        rs = session_power.query(Lines).filter(Lines.lines_voltage==voltage).all()
        return class_to_dict(rs)

    def add_line(self,user,line):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            session_power.add(line)
            session_power.commit()
            return 1
        else:
            return -1

    def add_lines(self,user,lines):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            for item in lines:
                session_power.add(item)
                session_power.commit()
                return 1
        else:
            return -1

class TowerDao:
    def query_towers_all(self):
        rs = session_power.query(Towers).filter(Towers.deleted==0).all()
        return class_to_dict(rs)

    def query_towers(self,linename):
        if linename is not None:
            rs = session_power.query(Towers).filter(Towers.tower_linename==linename,Towers.deleted==0).all()
            return class_to_dict(rs)
        else:
            return self.query_towers_all()

    def add_tower(self,user,tower):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            session_power.add(tower)
            session_power.commit()
            return 1
        else:
            return -1

    def add_towers(self,user,towers):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            for item in towers:
                session_power.add(item)
                session_power.commit()
                return 1
        else:
            return -1

    def del_tower(self,user,towersid):
        tower=session_power.query(Towers).filter(Towers.tower_id==towersid).first()
        tower.deleted=1
        session_power.commit()
        return 1

class PhotoDao:
    def query_photos(self):
        rs = session_power.query(Photo).all()
        return class_to_dict(rs)

    def query_photos(self,towerIdx):
        rs = session_power.query(Photo).filter(Photo.photo_tower_id==towerIdx).all()
        return class_to_dict(rs)

    def add_photo(self,user,photo):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            session_power.add(photo)
            session_power.commit()
            return 1
        else:
            return -1

    def add_photo(self,voltage,line_id,tower_id,classify,path):
        #是否进行判断
        line = session_power.query(Lines).filter(Lines.lines_id==line_id).first()
        photo = Photo(photo_line=line_id,photo_tower_id=tower_id,photo_path=path,photo_classify=classify)
        session_power.add(photo)
        session_power.commit()
        return 1

    def add_photos(self,user,photos):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            for item in photos:
                session_power.add(item)
                session_power.commit()
                return 1
        else:
            return -1