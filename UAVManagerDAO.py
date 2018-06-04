#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import math

reload(sys)
sys.setdefaultencoding('utf8')

import ConfigParser
import hashlib
import json
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker,query
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import  SignatureExpired,BadSignature
from UAVManagerEntity import User, Role, Role_basic, Manager,Battery,Device,Pad,Parts,Approval,Fault,FaultReport,Approval_db, class_to_dict

from flask import Flask, request ,jsonify
from flask import Response,make_response

cf = ConfigParser.ConfigParser()
cf.read("config.conf")
db_host = cf.get("db_uav", "db_host")
db_port = cf.getint("db_uav", "db_port")
db_user = cf.get("db_uav", "db_user")
db_pass = cf.get("db_uav", "db_pass")
db_name = cf.get("db_uav","db_name")

usr_host = cf.get("db_usr", "db_host")
usr_port = cf.getint("db_usr", "db_port")
usr_user = cf.get("db_usr", "db_user")
usr_pass = cf.get("db_usr", "db_pass")
usr_name = cf.get("db_usr","db_name")

secret_key = cf.get('token','SECRET_KEY')

engine_uav = create_engine('mysql+mysqldb://' + db_user + ':' + db_pass + '@' + db_host + ':' + str(db_port) + '/' + db_name+'?charset=utf8')
engine_usr = create_engine('mysql+mysqldb://' + usr_user + ':' + usr_pass + '@' + usr_host + ':' + str(usr_port) + '/' + usr_name+'?charset=utf8')
Session_UAV = sessionmaker(bind=engine_uav)
session_uav = Session_UAV()
Session_User = sessionmaker(bind=engine_usr)
session_usr = Session_User()


def md5_key(arg):
    hash = hashlib.md5()
    hash.update(arg)
    return hash.hexdigest()

class UserDAO:
    #verify passowrd
    def verify_password(self,username,password):
        if(not username or not password):
            return False

        usr=session_usr.query(User).filter(User.user_id==username).first()
        session_usr.rollback()
        if(not usr or usr.user_password!=md5_key(password)):
            return False
        else:
            return True
    #verify token
    def verify_token(self,token,password):
        if token is None:
            return None

        s=Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        usr=session_usr.query(User).filter(User.user_id == data['id']).first()
        session_usr.rollback()
        return usr

    #insert obj into table
    def insert_user(self,user,user_login):
        roles = self.get_role(user_login)
        if '5' in roles and '6' not in roles:
            if user.user_team==user_login.user_role:
                session_usr.add(user)
                try:
                    session_usr.commit()
                except:
                    session_usr.rollback()
                return rs
            else:
                return -1
        elif '6' in roles:
            session_usr.add(user)
            try:
                session_usr.commit()
            except:
                session_usr.rollback()
            return rs
        else:
            return -1
    
    #get obj by id
    def get_user_byId(self,userid):
        user=session_usr.query(User).filter(User.user_id==userid).first()
        session_usr.rollback()
        return user

    #get obj by name
    def get_user_byName(self,name):
        if(not name):
            return -1
        else:
            usr=session_usr.query(User).filter(User.user_id==name).first()
            session_usr.rollback()
            return usr

    #authority
    def get_role(self,user):
        rs = session_usr.query(Role).filter(Role.role_id==user.user_role).first()
        session_usr.rollback()
        role = rs.role_basic.split(',')
        return role

    def query_users(self,user):
        roles = self.get_role(user)
        if '5' in roles or '6' in roles:
            rs = session_usr.query(User).all()
            session_usr.rollback()
            return class_to_dict(rs)
        else:
            return None

class DeviceDAO:
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Device).filter(Device.user_team==user.user_team).all()
            session_uav.rollback()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Device).all()
            session_uav.rollback()
            return class_to_dict(rs)
        else:
            return None

    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Device).filter(Device.user_team==user.user_team).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Device).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    #查询页数
    def query_pages(self,user,device_type,device_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = session_uav.query(Device)
        if '1' in roles and '5' not in roles:
            q = q.filter(Device.user_team == user.user_team)
        if device_type:
            q = q.filter(Device.device_type == device_type)
        if device_status:
            q = q.filter(Device.device_status == device_status)
        rs = q.count()/page_size+1
        session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    def query_index(self,uav_id):
        return class_to_dict(session_uav.query(Device).filter(Device.device_id==uav_id).first())

    def query_condition(self,user,device_id,device_ver,device_type,uad_code,device_status,page_index,page_size):
        q = session_uav.query(Device)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None
        if '1' in roles and '5' not in roles:
            q = q.filter(Device.user_team == user.user_team)
        if device_ver:
            q = q.filter(Device.device_ver==device_ver)
        if device_id:
            q = q.filter(Device.device_id == device_id)
        if device_type:
            q = q.filter(Device.device_type == device_type)
        if uad_code:
            q = q.filter(Device.uad_code == uad_code)
        if device_status:
            q = q.filter(Device.device_status == device_status)
        device=q.limit(page_size).offset((page_index-1)*page_size).all()
        session_uav.rollback()
        return  class_to_dict(device)

    def query_statistic(self,user,device_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql=''
            if(device_status!='总数'):
                sql='select device_type,count(device_type) from tb_device where user_team=\''+user.user_team+'\'&& device_status=\''+device_status+'\' group by device_type;'
            else:
                sql = 'select device_type,count(device_type) from tb_device where user_team=\'' + user.user_team + '\' group by device_type;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql=''
            if(device_status!='总数'):
                sql='select device_type, count(device_type) from tb_device where device_status=\''+device_status+'\' group by device_type;'
            else:
                sql = 'select device_type, count(device_type) from tb_device group by device_type;'

            rs = session_uav.execute(sql).fetchall()
            session_uav.rollback()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_statistic_all(self,user):
        #get type first
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql = 'select device_type from tb_device where user_team=\'' + user.user_team + '\' group by device_type;'
            rs = session_uav.execute(sql).fetchall()
            session_uav.rollback()
            ret=[]
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(session_uav.query(Device).filter(Device.device_type==strType,Device.user_team==user.user_team).all())
                item['instock']=len(session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='在库',Device.user_team==user.user_team).all())
                item['removal'] = len(session_uav.query(Device).filter(Device.device_type == strType, Device.device_status == '出库',Device.user_team == user.user_team).all())
                item['maintain']=len(session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='维修',Device.user_team==user.user_team).all())
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql = 'select device_type from tb_device group by device_type;'
            rs = session_uav.execute(sql).fetchall()
            ret=[]
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(session_uav.query(Device).filter(Device.device_type==strType).all())
                item['instock']=len(session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='在库').all())
                item['removal'] = len(session_uav.query(Device).filter(Device.device_type == strType, Device.device_status == '出库').all())
                item['maintain']=len(session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='维修').all())

                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_type(self,user_team):
        sql = 'select device_type from tb_device group by device_type;'
        rs = session_uav.execute(sql).fetchall()
        session_uav.rollback()
        ret = []
        for i in rs:
            item = {}
            item['device_type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_ver(self):
        sql = 'select device_ver from tb_device group by device_ver;'
        rs = session_uav.execute(sql).fetchall()
        session_uav.rollback()
        ret = []
        for i in rs:
            item = {}
            item['device_ver'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_type(self):
        sql = 'select device_type from tb_device group by device_type;'
        rs = session_uav.execute(sql).fetchall()
        session_uav.rollback()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def add_device(self,usr,device):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            #首先判断无人机是否存在
            exist = session_uav.query(Device).filter(Device.device_id==device.device_id).first()
            if exist is not None:
                return -2
            #不存在则添加
            session_uav.add(device)
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_device(self,usr,device):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            uav=session_uav.query(Device).filter(Device.device_id == device.device_id).first()

            #无人机不存在
            if uav is None:
                return  -2

            #存在则修改
            uav.device_ver=device.device_ver
            uav.device_type=device.device_type
            uav.uad_code=device.uad_code
            uav.device_fact=device.device_fact
            uav.device_date=device.device_date
            uav.user_team=device.user_team
            uav.uad_camera=device.uad_camera
            uav.uav_yuntai=device.uav_yuntai
            uav.uad_rcontrol=device.uad_rcontrol

            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_device_status(self,usr,device_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            uav=session_uav.query(Device).filter(Device.device_id == device_id).first()
            uav.device_status=status
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

class BatteryDAO:
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Battery).filter(Battery.user_team==user.user_team).all()
            session_uav.rollback()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Battery).all()
            session_uav.rollback()
            return class_to_dict(rs)
        else:
            return None

    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Battery).filter(Battery.user_team==user.user_team).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Battery).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    def query_pages(self,user,battery_type,battery_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = session_uav.query(Battery)
        if '1' in roles and '5' not in roles:
            q = q.filter(Battery.user_team == user.user_team)
        if battery_type:
            q = q.filter(Battery.battery_type == battery_type)
        if battery_status:
            q = q.filter(Battery.battery_status == battery_status)
        rs = q.count()/page_size+1
        session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    def query_condition(self,user,bttery_id,bttery_ver,bttery_type,bttery_status,page_index,page_size):
        q = session_uav.query(Battery)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None
        if '1' in roles and '5' not in roles:
            q = q.filter(Battery.user_team == user.user_team)
        if bttery_ver:
            q = q.filter(Battery.battery_ver==bttery_ver)
        if bttery_id:
            q = q.filter(Battery.battery_id == bttery_id)
        if bttery_type:
            q = q.filter(Battery.battery_type == bttery_type)
        if bttery_status:
            q = q.filter(Battery.battery_status == bttery_status)
        battery=q.limit(page_size).offset((page_index-1)*page_size).all()
        session_uav.rollback()
        return class_to_dict(battery)

    def query_statistic(self,user,bttery_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql=''
            if(bttery_status!='总数'):
                sql='select battery_type,count(battery_type) from tb_battery where user_team=\''+user.user_team+'\'&& battery_status=\''+bttery_status+'\' group by battery_type;'
            else:
                sql = 'select battery_type,count(battery_type) from tb_battery where user_team=\'' + user.user_team + '\' group by battery_type;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
            return rs
        elif '5' in roles:
            sql=''
            if(bttery_status!='总数'):
                sql='select battery_type, count(battery_type) from tb_battery where battery_status=\''+bttery_status+'\' group by battery_type;'
            else:
                sql = 'select battery_type, count(battery_type) from tb_battery group by battery_type;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_statistic_all(self,user):
        #get type first
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql = 'select battery_type from tb_battery where user_team=\'' + user.user_team + '\' group by battery_type;'
            rs = session_uav.execute(sql).fetchall()
            ret=[]
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.user_team==user.user_team).all())
                item['instock']=len(session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='在库',Battery.user_team==user.user_team).all())
                item['removal']=len(session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='出库',Battery.user_team==user.user_team).all())
                item['maintain']=len(session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='维修',Battery.user_team==user.user_team).all())
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql = 'select battery_type from tb_battery group by battery_type;'
            rs = session_uav.execute(sql).fetchall()
            ret=[]
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(session_uav.query(Battery).filter(Battery.battery_type==strType).all())
                item['instock']=len(session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='在库').all())
                item['removal'] = len(session_uav.query(Battery).filter(Battery.battery_type == strType, Battery.battery_status == '出库').all())
                item['maintain']=len(session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='维修').all())
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_type(self,user_team):
        sql = 'select battery_type from tb_battery where user_team=\'' + user_team + '\' group by battery_type;'
        rs = session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['battery_type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_type(self):
        sql = 'select battery_type from tb_battery group by battery_type;'
        rs = session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def add_battery(self,usr,battery):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            #首先判断是否存在
            exist = session_uav.query(Battery).filter(Battery.battery_id==battery.battery_id).first()
            if exist is not None:
                return -2

            session_uav.add(battery)
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_battery(self,usr,battery):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            batteryobj=session_uav.query(Battery).filter(Battery.battery_id == battery.battery_id).first()
            if batteryobj is None:
                return -2

            batteryobj.battery_ver = battery.battery_ver
            batteryobj.battery_type = battery.battery_type
            batteryobj.battery_fact = battery.battery_fact
            batteryobj.battery_date = battery.battery_date
            batteryobj.user_team = battery.user_team
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_battery_status(self,usr,battery_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            battery=session_uav.query(Battery).filter(Battery.battery_id==battery_id).first()
            battery.battery_status=status
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

class PadDao:
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Pad).filter(Pad.user_team==user.user_team).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Pad).all()
            return class_to_dict(rs)
        else:
            return None

    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Pad).filter(Pad.user_team==user.user_team).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Pad).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    def query_pages(self,user,pad_type,pad_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = session_uav.query(Pad)
        if '1' in roles and '5' not in roles:
            q = q.filter(Pad.user_team == user.user_team)
        if pad_type:
            q = q.filter(Pad.pad_type == pad_type)
        if pad_status:
            q = q.filter(Pad.pad_status == pad_status)
        rs = q.count()/page_size+1
        session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    def query_condition(self, user, pad_id, pad_ver, pad_type, pad_status, page_index, page_size):
        q = session_uav.query(Pad)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None
        if '1' in roles and '5' not in roles:
            q = q.filter(Pad.user_team == user.user_team)
        if pad_ver:
            q = q.filter(Pad.pad_ver==pad_ver)
        if pad_id:
            q = q.filter(Pad.pad_id == pad_id)
        if pad_type:
            q = q.filter(Pad.pad_type == pad_type)
        if pad_status:
            q = q.filter(Pad.pad_status == pad_status)
        pad=q.limit(page_size).offset((page_index-1)*page_size).all()
        return  class_to_dict(pad)

    def query_statistic(self,user,pad_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql=''
            if(pad_status!='总数'):
                sql='select pad_type,count(pad_type) from tb_pad where user_team=\''+user.user_team+'\'&& pad_status=\''+pad_status+'\' group by pad_type;'
            else:
                sql = 'select pad_type,count(pad_type) from tb_pad where user_team=\'' + user.user_team + '\' group by pad_type;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql=''
            if(pad_status!='总数'):
                sql='select pad_type, count(pad_type) from tb_pad where pad_status=\''+pad_status+'\' group by pad_type;'
            else:
                sql = 'select pad_type, count(pad_type) from tb_pad group by pad_type;'

            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_type(self):
        sql = 'select pad_type from tb_pad group by pad_type;'
        rs = session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def add_pad(self,usr,pad):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            existed = session_uav.query(Pad).filter(Pad.pad_id==pad.pad_id).first()
            session_uav.rollback()
            if(existed is not None):
                return -2
            session_uav.add(pad)
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_pad(self,usr,pad):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            padtmp=session_uav.query(Pad).filter(Pad.pad_id == pad.pad_id).first()
            padtmp.pad_ver = pad.pad_ver
            padtmp.pad_type = pad.pad_type
            padtmp.pad_fact = pad.pad_fact
            padtmp.pad_date = pad.pad_date
            padtmp.user_team = pad.user_team
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_pad_status(self,usr,pad_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            pad=session_uav.query(Pad).filter(Pad.pad_id == pad_id).first()
            pad.pad_status=status
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

#配件
class PartsDao:
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            return class_to_dict(session_uav.query(Parts).all())
        else:
            return None

    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=session_uav.query(Parts).filter(Parts.user_team==user.user_team).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = session_uav.query(Parts).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    def query_pages(self,user,parts_type,parts_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = session_uav.query(Parts)
        if '1' in roles and '5' not in roles:
            q = q.filter(Parts.user_team == user.user_team)
        if parts_type:
            q = q.filter(Parts.parts_type == parts_type)
        if parts_status:
            q = q.filter(Parts.parts_status == parts_status)
        rs = q.count()/page_size+1
        session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    def query_statistic(self,user,part_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql=''
            if(part_status!='总数'):
                sql='select parts_type,count(parts_type) from tb_parts where user_team=\''+user.user_team+'\'&& parts_status=\''+part_status+'\' group by device_type;'
            else:
                sql = 'select parts_type,count(parts_type) from tb_parts where user_team=\'' + user.user_team + '\' group by parts_type;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql=''
            if(part_status!='总数'):
                sql='select parts_type, count(parts_type) from tb_parts where parts_status=\''+part_status+'\' group by parts_type;'
            else:
                sql = 'select parts_type, count(parts_type) from tb_parts group by parts_type;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_type(self):
        sql = 'select parts_type from tb_parts group by parts_type;'
        rs = session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def query_condition(self,user,parts_id,parts_ver,parts_type,parts_status,page_index,page_size):
        q = session_uav.query(Parts)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        sql = 'select * from tb_device where '
        if '1' not in roles:
            return None
        if '1' in roles and '5' not in roles:
            q = q.filter(Parts.user_team == user.user_team)
        if parts_ver:
            q = q.filter(Parts.parts_ver==parts_ver)
        if parts_id:
            q = q.filter(Parts.parts_id == parts_id)
        if parts_type:
            q = q.filter(Parts.parts_type == parts_type)
        if parts_status:
            q = q.filter(Parts.parts_status == parts_status)
        parts=q.limit(page_size).offset((page_index-1)*page_size).all()
        return  class_to_dict(parts)

    def add_parts(self,usr,parts):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            exist = session_uav.query(Parts).filter(Parts.parts_id==parts.parts_id).first()
            if exist is not None:
                return -2

            session_uav.add(parts)
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_parts(self,usr,parts):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            partstmp=session_uav.query(Parts).filter(Parts.parts_id==parts.parts_id).first()
            if partstmp is None:
                return -2

            partstmp.parts_ver = parts.parts_ver
            partstmp.parts_type = parts.parts_type
            partstmp.parts_fact = parts.parts_fact
            partstmp.parts_date = parts.parts_date
            partstmp.user_team = parts.user_team
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

    def modify_parts_status(self,usr,parts_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            parts=session_uav.query(Parts).filter(Parts.parts_id==parts_id).first()
            parts.parts_status=status
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

#出入库管理
class ManagerDAO:
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            return class_to_dict(session_uav.query(Manager).all())
        else:
            return None

    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            return class_to_dict(session_uav.query(Manager).limit(page_size).offset((page_index-1)*page_size).all())
        else:
            return None

    def query_pages(self,user,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles or '5' in roles:
            rs=session_uav.query(Manager).count()/page_size+1
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        else:
            return None

    #def query_index(self,device_id):


    def query_borrow(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        #只能看到本班组设备的借用情况
        if '1' in roles:
            return class_to_dict(session_uav.query(Manager).filter(Manager.manager_status=='借用',Manager.user_team==user.user_team).all())
        else:
            return None

    def query_condition(self,user,device_ver,device_id,device_type,manager_status,borrow_time,return_time,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            q = session_uav.query(Manager)
            if device_ver:
                q = q.filter(Manager.device_ver==device_ver)
            if device_id:
                q = q.filter(Manager.device_id == device_id)
            if device_type:
                q = q.filter(Manager.device_type == device_type)
            if manager_status:
                q = q.filter(Manager.manager_status == manager_status)
            if borrow_time:
                q = q.filter(Manager.borrower_date == borrow_time)
            if return_time:
                q = q.filter(Manager.return_date == return_time)
            mngr=q.limit(page_size).offset((page_index-1)*page_size).all()
            return  class_to_dict(mngr)
        else:
            return None;

    #借用的判断逻辑为：首先判断借用人和借用设备是否是同一个班组
    #   不是同一个班组则判断是否提交借调申请
    #       提交了借调申请则判断当前用户是否有权限批准
    #       未提交借调申请返回错误
    #   是同一个班组
    #       当前用户是否有权限批准
    #       无权限批准则返回错误
    def manager_borrow(self,user,approver,borrower,borrow_team,uav_id,borrow_time,return_time):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        #判断设备类型
        device = session_uav.query(Device).filter(Device.device_id == uav_id).first()
        battery = session_uav.query(Battery).filter(Battery.battery_id == uav_id).first()
        part = session_uav.query(Parts).filter(Parts.parts_id == uav_id).first()
        pad = session_uav.query(Pad).filter(Pad.pad_id == uav_id).first()
        idx = 0
        user_team=''
        status = ''
        if device:
            idx = 1
            user_team = device.user_team
            status = device.device_status
        if battery:
            idx = 2
            user_team = battery.user_team
            status = battery.battery_status
        if part:
            idx = 3
            user_team = part.user_team
            status = part.parts_status
        if pad:
            idx = 4
            user_team = pad.user_team
            status = pad.pad_status
        if status!='在库':
            return -2#设备未归还
        if idx==0:
            return -1

        #判断是否是一个班组
        usr=session_usr.query(User).filter(User.user_name==borrower).first()
        session_usr.rollback()
        #如果用户不存在
        if usr==None:
            return -1

        #如果不是同一班组
        if usr.user_team!=user_team:
            #是否经过审批流程
            approve=session_uav.query(Approval).filter(Approval.apply_person==usr.user_name).first()
            if(approve != None):
                if(Approval.approval_status==1):
                    if '4' in roles:
                        #审批人是否有权限审批借出
                        if user.user_team==user_team: #有
                            if idx==1:
                                obj = Manager(device_id=uav_id, device_ver=device.device_ver,device_type=device.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                                session_uav.add(obj)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                session_uav.query(Device).filter(Device.device_id == uav_id).update({Device.device_status: '出库', Device.device_use_number: device.device_use_number + 1},synchronize_session=False)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                return 1
                            if idx==2:
                                obj = Manager(device_id=uav_id, device_ver=battery.device_ver,device_type=battery.device_type, approver_name=approver, borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用', return_date=return_time)
                                session_uav.add(obj)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                session_uav.query(Battery).filter(Battery.battery_id == uav_id).update({Battery.battery_status: '出库', Battery.battery_use_number: battery.device_use_number + 1},synchronize_session=False)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                return 1
                            if idx==3:
                                obj = Manager(device_id=uav_id, device_ver=part.device_ver,device_type=part.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                                session_uav.add(obj)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                session_uav.query(Parts).filter(Parts.parts_id == uav_id).update({Parts.parts_status: '出库', Parts.parts_use_number: part.parts_use_number + 1},synchronize_session=False)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                return 1
                            if idx==4:
                                obj = Manager(device_id=uav_id, device_ver=pad.device_ver,device_type=pad.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                                session_uav.add(obj)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                session_uav.query(Pad).filter(Pad.pad_id == uav_id).update({Pad.pad_status: '出库', Pad.pad_use_number: pad.pad_use_number + 1},synchronize_session=False)
                                try:
                                    session_uav.commit()
                                except:
                                    session_uav.rollback()
                                return 1
                            #借调申请记录的处理
                            approvalDao = ApprovalDao()
                            approvalDao.approval_finished(approve.apply_person)
                        else:#无
                            return -1
                    elif(Approval.approval_status==0):
                        #未审批
                        return -1
                    else:
                        #审批不通过
                        approvalDao = ApprovalDao()
                        approvalDao.approval_finished(approve.apply_person)
                elif '5' in roles:
                    if idx == 1:
                        obj = Manager(device_id=uav_id, device_ver=device.device_ver, device_type=device.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Device).filter(Device.device_id == uav_id).update({Device.device_status: '出库', Device.device_use_number: device.device_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    if idx == 2:
                        obj = Manager(device_id=uav_id, device_ver=battery.device_ver,device_type=battery.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Battery).filter(Battery.battery_id == uav_id).update({Battery.battery_status: '出库', Battery.battery_use_number: battery.device_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    if idx == 3:
                        obj = Manager(device_id=uav_id, device_ver=part.device_ver,device_type=part.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Parts).filter(Parts.parts_id == uav_id).update({Parts.parts_status: '出库', Parts.parts_use_number: part.parts_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    if idx == 4:
                        obj = Manager(device_id=uav_id, device_ver=pad.device_ver,device_type=pad.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Pad).filter(Pad.pad_id == uav_id).update({Pad.pad_status: '出库', Pad.pad_use_number: pad.pad_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    return 1
                else:
                    return -1
            else:
                return -1
        else:#同一班组
            if '4' in roles:
                if user.user_team==user_team:#是否是班组管理员
                    if idx == 1:
                        obj = Manager(device_id=uav_id, device_ver=device.device_ver,device_type=device.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用', return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Device).filter(Device.device_id == uav_id).update({Device.device_status: '出库', Device.device_use_number: device.device_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    if idx == 2:
                        obj = Manager(device_id=uav_id, device_ver=battery.device_ver,device_type=battery.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Battery).filter(Battery.battery_id == uav_id).update({Battery.battery_status: '出库', Battery.battery_use_number: battery.device_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    if idx == 3:
                        obj = Manager(device_id=uav_id, device_ver=part.device_ver,device_type=part.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Parts).filter(Parts.parts_id == uav_id).update({Parts.parts_status: '出库', Parts.parts_use_number: part.parts_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                    if idx == 4:
                        obj = Manager(device_id=uav_id, device_ver=pad.device_ver, device_type=pad.device_type, approver_name=approver, borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                        session_uav.add(obj)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        session_uav.query(Pad).filter(Pad.pad_id == uav_id).update({Pad.pad_status: '出库', Pad.pad_use_number: pad.pad_use_number + 1},synchronize_session=False)
                        try:
                            session_uav.commit()
                        except:
                            session_uav.rollback()
                        return 1
                else:
                    return -1
            elif '5' in roles:#管理员权限
                if idx == 1:
                    obj = Manager(device_id=uav_id, device_ver=device.device_ver,device_type=device.device_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                    session_uav.add(obj)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    if  device.device_use_number is None:
                        session_uav.query(Device).filter(Device.device_id == int(uav_id)).update({Device.device_status: '出库', Device.device_use_number: 1},synchronize_session=False)
                    else:
                        session_uav.query(Device).filter(Device.device_id == int(uav_id)).update({Device.device_status: '出库', Device.device_use_number: device.device_use_number + 1},synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    return 1
                if idx == 2:
                    obj = Manager(device_id=uav_id, device_ver=battery.battery_ver,device_type=battery.battery_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用', return_date=return_time)
                    session_uav.add(obj)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    session_uav.query(Battery).filter(Battery.battery_id == uav_id).update({Battery.battery_status: '出库', Battery.battery_use_number: battery.battery_use_number + 1},synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    return 1
                if idx == 3:
                    obj = Manager(device_id=uav_id, device_ver=part.parts_ver,device_type=part.parts_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                    session_uav.add(obj)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    session_uav.query(Parts).filter(Parts.parts_id == uav_id).update( {Parts.parts_status: '出库', Parts.parts_use_number: part.parts_use_number + 1},synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    return 1
                if idx == 4:
                    obj = Manager(device_id=uav_id, device_ver=pad.pad_ver,device_type=pad.pad_type, approver_name=approver,borrower_name=borrower,borrow_date=borrow_time, user_team=borrow_team, manager_status='借用',return_date=return_time)
                    session_uav.add(obj)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    session_uav.query(Pad).filter(Pad.pad_id == uav_id).update({Pad.pad_status: '出库', Pad.pad_use_number: pad.pad_use_number + 1},synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                    return 1
            else:
                return -1

    def manager_return(self,user,device_id,return_date,return_desc):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '4' in roles or '5' in roles:
            device = session_uav.query(Device).filter(Device.device_id==device_id).first()
            battery= session_uav.query(Battery).filter(Battery.battery_id==device_id).first()
            part   = session_uav.query(Battery).filter(Parts.parts_id==device_id).first()
            pad = session_uav.query(Battery).filter(Pad.pad_id == device_id).first()
            manager = session_uav.query(Manager).filter(Manager.device_id==device_id,Manager.manager_status=='借用').first()
            idx=0
            if device:
                idx=1
            if battery:
                idx=2
            if part:
                idx=3
            if pad:
                idx=4

            if not manager:
                return -1

            if idx!=0:
                session_uav.query(Manager).filter(Manager.device_id == manager.device_id and Manager.manager_status=='借用').update({Manager.manager_status: '归还',Manager.return_date:return_date,Manager.return_desc:return_desc}, synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            else:
                return -1

            if idx==1:
                session_uav.query(Device).filter(Device.device_id == manager.device_id).update({Device.device_status: '在库'},synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            if idx==2:
                session_uav.query(Battery).filter(Battery.battery_id == manager.device_id).update({Battery.battery_status: '在库'},synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            if idx==3:
                session_uav.query(Parts).filter(Parts.parts_id == manager.device_id).update({Parts.parts_status: '在库'},synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            if idx==4:
                session_uav.query(Pad).filter(Pad.pad_id == manager.device_id).update({Pad.pad_status: '在库'},synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            return 1

    def manager_query_device(self,device_id,retruntime,borrower):
        device = session_uav.query(Device).filter(Device.device_id == device_id).first()
        battery = session_uav.query(Battery).filter(Battery.battery_id == device_id).first()
        part = session_uav.query(Battery).filter(Parts.parts_id == device_id).first()
        pad = session_uav.query(Battery).filter(Pad.pad_id == device_id).first()
        session_uav.rollback()
        idx = 0
        if device:
            idx = 1
        if battery:
            idx = 2
        if part:
            idx = 3
        if pad:
            idx = 4

        if idx==0:
            return  None

        ret = []
        deviceitem = {}

        if idx==1:
            uav_dao = DeviceDAO()
            uav = uav_dao.query_index(device_id)
            deviceitem['device_type'] = uav['device_type']
            deviceitem['device_id'] = uav['device_id']
            deviceitem['user_team'] = uav['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower

        elif idx==2:
            battery = class_to_dict(session_uav.query(Battery).filter(Battery.battery_id==device_id).all())
            deviceitem['device_type'] = battery[0]['battery_type']
            deviceitem['device_id'] = battery[0]['battery_id']
            deviceitem['user_team'] = battery[0]['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower

        elif idx==3:
            part = class_to_dict(session_uav.query(Parts).filter(Parts.parts_id==device_id).all())
            deviceitem['device_type'] = part[0]['parts_type']
            deviceitem['device_id'] = part[0]['parts_id']
            deviceitem['user_team'] = part[0]['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower
        else:
            pad = class_to_dict(session_uav.query(Pad).filter(Pad.pad_id==device_id).all())
            deviceitem['device_type'] = pad[0]['pad_type']
            deviceitem['device_id'] = pad[0]['pad_id']
            deviceitem['user_team'] = pad[0]['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower
        ret.append(deviceitem)
        return ret

#故障管理
class FaultDao:
    def query_list(self,user,device_ver,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = session_uav.query(Fault)
        if device_ver:
            q = q.filter(Fault.device_ver == device_ver)
        allFaults = q.limit(page_size).offset((page_index-1)*page_size).all()
        session_uav.rollback()
        return class_to_dict(allFaults)

    def query_pages(self,device_ver,page_size):
        if device_ver is not None:
            rs= session_uav.query(Fault).filter(Fault.device_ver==device_ver).count() / page_size + 1
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        else:
            if page_size>0:
                rs= session_uav.query(Fault).count()/page_size+1
                item = {}
                item['pages'] = rs
                return json.dumps(item)
            else:
                return None

    def query_statistics(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            #故障原因
            sql = 'select fault_reason,count(*) from tb_fault group by fault_reason;'
            rs = session_uav.execute(sql).fetchall()
            session_uav.rollback()

            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql = 'select fault_reason, count(*) from tb_fault group by fault_reason;'
            rs = session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    def query_types(self):
        sql = 'select device_ver from tb_fault group by device_ver;'
        rs = session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['device_ver'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    def add_fault(self,user,fault):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)

        device = session_uav.query(Device).filter(Device.device_id == fault.device_id).first()
        battery = session_uav.query(Battery).filter(Battery.battery_id == fault.device_id).first()
        part = session_uav.query(Battery).filter(Parts.parts_id == fault.device_id).first()
        pad = session_uav.query(Battery).filter(Pad.pad_id == fault.device_id).first()

        idx = 0
        if device:
            idx = 1
        if battery:
            idx = 2
        if part:
            idx = 3
        if pad:
            idx = 4
        if idx==0:
            return -2

        if '2' in roles and '5' not in roles:
            if device.user_team==user.user_team:
                session_uav.add(fault)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
                if idx == 1:
                    session_uav.query(Device).filter(Device.device_id == fault.device_id).update(
                        {Device.device_status: '维修'}, synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                if idx == 2:
                    session_uav.query(Battery).filter(Battery.battery_id == fault.device_id).update(
                        {Battery.battery_status: '维修'}, synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                if idx == 3:
                    session_uav.query(Parts).filter(Parts.parts_id == fault.device_id).update(
                        {Parts.parts_status: '维修'}, synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                if idx == 4:
                    session_uav.query(Pad).filter(Pad.pad_id == fault.device_id).update({Pad.pad_status: '维修'},
                                                                                          synchronize_session=False)
                    try:
                        session_uav.commit()
                    except:
                        session_uav.rollback()
                return 1
            else :
                return -1
        if '5' in roles:
            session_uav.add(fault)
            try:
                session_uav.commit()
            except:
                session_uav.rollback()

            if idx == 1:
                session_uav.query(Device).filter(Device.device_id == fault.device_id).update(
                    {Device.device_status: '维修'}, synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            if idx == 2:
                session_uav.query(Battery).filter(Battery.battery_id == fault.device_id).update(
                    {Battery.battery_status: '维修'}, synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            if idx == 3:
                session_uav.query(Parts).filter(Parts.parts_id == fault.device_id).update(
                    {Parts.parts_status: '维修'}, synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            if idx == 4:
                session_uav.query(Pad).filter(Pad.pad_id == fault.device_id).update({Pad.pad_status: '维修'},
                                                                                    synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()
            return 1

        return -1

class FaultReportDao:
    def query(self,fpid):
        rs = session_uav.query(FaultReport).filter(FaultReport.fault_report_id==fpid).all()
        return class_to_dict(rs)

    def update(self,user,faultreport):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            rs = session_uav.query(FaultReport).filter(FaultReport.fault_report_id == faultreport.fault_report_id).first()
            rs.fault_report_device_id = faultreport.fault_report_device_id
            rs.fault_report_line_name = faultreport.fault_report_line_name
            rs.fault_report_towerRange = faultreport.fault_report_towerRange
            rs.fault_report_date = faultreport.fault_report_date
            rs.fault_report_flyer = faultreport.fault_report_flyer
            rs.fault_report_wether = faultreport.fault_report_wether
            rs.fault_report_observer = faultreport.fault_report_observer
            rs.fault_time = faultreport.fault_time
            rs.fault_crash_position = faultreport.fault_crash_position
            rs.fault_crash_desc = faultreport.fault_crash_desc
            rs.fault_crash_operation = faultreport.fault_crash_operation
            rs.fault_crash_damage = faultreport.fault_crash_damage
            rs.fault_crash_electric = faultreport.fault_crash_electric
            rs.fault_crash_around = faultreport.fault_crash_around
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -1

#借调申请管理
class ApprovalDao:
    def approval_query(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '4' in roles and  '5' not in roles:
            rs=session_uav.query(Approval).filter(Approval.approval_team==user.user_team,Approval.approval_status==0).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs=session_uav.query(Approval).filter(Approval.approval_status==0).all()
            return class_to_dict(rs)
        else:
            return None

    def approval_query_apply(self,user):
        rs=session_uav.query(Approval).filter(Approval.apply_person==user.user_name).all()
        return class_to_dict(rs)

    def approval_query_approve(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '4' in roles and  '5' not in roles:
            rs=session_uav.query(Approval).filter(Approval.approval_team==user.user_team).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs=session_uav.query(Approval).filter(Approval.approval_status==0).all()
            return class_to_dict(rs)
        else:
            return None       

    #批准借调
    def approval_aggree(self,user,approval):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)

        if '4' in roles and '5' not in roles:
            if user.user_team == approval.approval_team:
                session_uav.query(Approval).filter(Approval.apply_person == approval.apply_person).update(
                    {Approval.approval_status: 1}, synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()

    def approval_disagree(self,user,approval):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)

        if '4' in roles and '5' not in roles:
            if user.user_team == approval.approval_team:
                session_uav.query(Approval).filter(Approval.apply_person == approval.apply_person).update(
                    {Approval.approval_status: 2}, synchronize_session=False)
                try:
                    session_uav.commit()
                except:
                    session_uav.rollback()

    def approval_add(self,user,approval):
        usrDao=UserDAO()

        #提交的批准人无权限批准
        userApproval=session_usr.query(User).filter(User.user_name==approval.approval_person).first()
        if userApproval is None:
            return -2
        roleApproval = usrDao.get_role(userApproval)
        if '4' not in roleApproval and '5' not in roleApproval:
            return -2

        roles=usrDao.get_role(user)
        if '4' in roles or '5' in roles:
            if user.user_team==approval.approval_team:
                return -1

            approvalTmp = session_uav.query(Approval).filter(Approval.apply_person==approval.apply_person).first()
            #提交申请后申请未审核则状态为0，审核通过则状态为1，审核未空过则状态为2
            #在提交新的申请时首先判断原有申请是否处理，如果未处理则先处理原有申请
            if(approvalTmp !=None and approvalTmp.approval_status!=0):
                self.approval_finished(approval.apply_person)
            
            session_uav.merge(approval)
            try:
                session_uav.commit()
            except:
                session_uav.rollback()
            return 1
        else:
            return -2

    #将申请添加到申请处理备份库中
    def approval_finished(self,apply_person):
        approval_cur = session_uav.query(Approval).filter(Approval.apply_person==apply_person).first()
        approval_db=Approval_db()
        approval_db.apply_person=approval_cur.apply_person
        approval_db.approval_person=approval_cur.approval_person
        approval_db.approval_team=approval_cur.approval_team
        approval_db.device_ver=approval_cur.device_ver
        approval_db.device_number=approval_cur.device_number
        approval_db.battery_ver = approval_cur.battery_ver
        approval_db.battery_number=approval_cur.battery_number
        approval_db.pad_ver = approval_cur.pad_ver
        approval_db.pad_number=approval_cur.pad_number
        approval_db.approval_status=approval_cur.approval_status

        session_uav.add(approval_db)
        try:
            session_uav.commit()
        except:
            session_uav.rollback()
        session_uav.delete(approval_cur)
        try:
            session_uav.commit()
        except:
            session_uav.rollback()
