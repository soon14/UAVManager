#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:此文件为数据操作接口，主要是对用户信息，无人机、电池、配件、平板等设备进行管理，
     对无人机故障等信息进行管理；采用的SQL中间件为为SQLAlchemy；

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
import hashlib
import json
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker,query
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import  SignatureExpired,BadSignature
from UAVManagerEntity import User, Role, Role_basic, Manager,Battery,Device,Pad,Parts,Approval,Fault,FaultReport,Approval_db,Plan, class_to_dict

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

engine_uav = create_engine('mysql+mysqldb://' + db_user + ':' + db_pass + '@' + db_host + ':' + str(db_port) + '/' + db_name+'?charset=utf8',pool_size=100,pool_recycle=3600)
engine_usr = create_engine('mysql+mysqldb://' + usr_user + ':' + usr_pass + '@' + usr_host + ':' + str(usr_port) + '/' + usr_name+'?charset=utf8',pool_size=100,pool_recycle=3600)
Session_UAV = sessionmaker(bind=engine_uav)
Session_User = sessionmaker(bind=engine_usr)

#进行md5加密
#param arg:输入需要加密的参数
#return :输出加密后的数据
def md5_key(arg):
    hash = hashlib.md5()
    hash.update(arg)
    return hash.hexdigest()

#用户操作类
# 主要定义用户数据的操作，包括增改删查等
#author:Wu Wei
#Version 1.0.0.0
#所有错误代码以0101XXXX开始
class UserDAO:
    def __init__(self):
        self.session_usr=Session_User()
    
    def __del__(self):
        self.session_usr.close()
    
    #verify passowrd,确认用户名和密码登录
    #param username:输入用户名
    #param password:输入密码
    #return: 正确返回True 错误返回False
    def verify_password(self,username,password):
        if(not username or not password):
            return False

        usr=self.session_usr.query(User).filter(User.user_id==username).first()
        self.session_usr.rollback()
        if(not usr or usr.user_password!=md5_key(password)):
            return False
        else:
            return True

    #verify token 确认token直接导入token解析是否正确
    #param token 输入token
    #param password 输入密码（可以不需要输入）
    def verify_token(self,token,password):
        if token is None:
            return None

        s=Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return 1010301 # valid token, but expired
        except BadSignature:
            return 1010302 # invalid token
        usr=self.session_usr.query(User).filter(User.user_id == data['id']).first()
        self.session_usr.rollback()
        return usr

    #insert obj into table 插入用户
    #param user:需要插入的用户
    #param user_login:登录的用户
    def insert_user(self,user,user_login):
        roles = self.get_role(user_login)
        if '4' in roles and '5' not in roles and '6' not in roles:
            if user.user_team==user_login.user_team:
                exist=self.session_usr.query(User).filter(User.user_id==user.user_id).first()
                if exist is not None:
                    return 1010401
                user.user_password=md5_key(user.user_password)
                self.session_usr.add(user)
                try:
                    self.session_usr.commit()
                except:
                    self.session_usr.rollback()
                return 1
            else:
                return 1010402
        elif '6' in roles or '5' in roles:
            exist = self.session_usr.query(User).filter(User.user_id == user.user_id).first()
            if exist is not None:
                return 1010403

            user.user_password = md5_key(user.user_password)
            self.session_usr.add(user)
            try:
                self.session_usr.commit()
            except:
                self.session_usr.rollback()
            return 1
        else:
            return 1010404

    #修改用户信息
    #param user:修改后的用户信息
    #param user_login:登录的用户
    def modify_user(self,user,user_login):
        roles = self.get_role(user_login)
        if '4' in roles and '5' not in roles and '6' not in roles:
            if user.user_team==user_login.user_team:
                exist=self.session_usr.query(User).filter(User.user_id==user.user_id).first()
                if exist is None:
                    return 1010501
                if user.user_team!=user_login.user_team or user.user_department==user_login.user_department:
                    return 1010502

                user.user_password=md5_key(user.user_password)
                exist.user_id=user.user_id
                exist.user_password=user.user_password
                exist.user_name =user.user_name
                exist.user_phone =user.user_phone
                exist.user_number =user.user_number
                exist.user_department =user.user_department
                exist.user_team =user.user_team
                exist.user_role = user.user_role
                try:
                    self.session_usr.commit()
                except:
                    self.session_usr.rollback()
                return 1
            else:
                return 1010503
        elif '6' in roles or '5' in roles:
            exist = self.session_usr.query(User).filter(User.user_id == user.user_id).first()
            if exist is None:
                return 1010504
            user.user_password = md5_key(user.user_password)
            exist.user_id = user.user_id
            exist.user_password = user.user_password
            exist.user_name = user.user_name
            exist.user_phone = user.user_phone
            exist.user_number = user.user_number
            exist.user_department = user.user_department
            exist.user_team = user.user_team
            exist.user_role = user.user_role
            try:
                self.session_usr.commit()
            except:
                self.session_usr.rollback()
            return 1
        else:
            return 1010505

    #根据用户id获取用户信息（没有验证）
    #param userid:输入用户id
    #返回用户信息
    def get_user_byId(self,userid):
        user=self.session_usr.query(User).filter(User.user_id==userid).all()
        self.session_usr.rollback()
        return class_to_dict(user)

    #删除用户
    #param user:登录的用户
    #param userid:需要删除的用户的id
    def delete_user_byId(self,user,userid):
        roles = self.get_role(user.user_role)
        if '6' in roles:
            tmpUsr = self.session_usr.query(User.user_id==userid).first()
            self.session_usr.delete(tmpUsr)
            try:
                self.session_usr.commit()
            except:
                self.session_usr.rollback()
            return 1

    #get obj by name 根据用户名获取用户
    #param name:用户名
    #返回用户信息
    def get_user_byName(self,name):
        if(not name):
            return 1010805
        else:
            usr=self.session_usr.query(User).filter(User.user_id==name).first()
            self.session_usr.rollback()
            return usr

    #authority 获取用户权限
    #param user:输入用户
    #返回用户基础权限集合
    def get_role(self,user):
        rs = self.session_usr.query(Role).filter(Role.role_id==user.user_role).first()
        self.session_usr.rollback()
        role = rs.role_basic.split(',')
        return role

    #查询用户列表（分页查询）
    #param user:当前登录用户信息
    #param department:筛选部门(为空则所有部门)
    #param team:筛选班组(为空则所有班组)
    #page_index:查询第几页
    #page_size:每页展示数据条数
    #用户列表信息
    def query_users(self,user,department,team,page_index,page_size):
        roles = self.get_role(user)
        if '4' in roles and '5' not in roles and '6' not in roles:
            q=self.session_usr.query(User)
            if department is not None:
                q=q.filter(User.user_department==department)
            if team is not None:
                q=q.filter(User.user_team==team)
            rs = q.filter(User.user_team==user.user_team,User.user_department==user.user_department).limit(page_size).offset((page_index-1)*page_size).all()
            self.session_usr.rollback()
            return class_to_dict(rs)
        elif '5' in roles or '6' in roles:
            q=self.session_usr.query(User)
            if department is not None:
                q=q.filter(User.user_department==department)
            if team is not None:
                q=q.filter(User.user_team==team)
            rs = q.limit(page_size).offset((page_index-1)*page_size).all()
            self.session_usr.rollback()
            return class_to_dict(rs)
        else:
            return None

    #查询获取用户列表页数
    #param user:当前登录用户信息
    #param department:筛选部门(为空则所有部门)
    #param team:筛选班组(为空则所有班组)
    #page_size:每页展示数据条数
    #用户一共多少页
    def query_users_pages(self,user,department,team,page_size):
        roles = self.get_role(user)
        if '4' in roles and '5' not in roles and '6' not in roles:
            q=self.session_usr.query(User)
            if department is not None:
                q=q.filter(User.user_department==department)
            if team is not None:
                q=q.filter(User.user_team==team)
            rs = q.filter(User.user_team==user.user_team).count()/page_size+1
            self.session_usr.rollback()
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        if '5' in roles or '6' in roles:
            q=self.session_usr.query(User)
            if department is not None:
                q=q.filter(User.user_department==department)
            if team is not None:
                q=q.filter(User.user_team==team)
            rs = q.count()/page_size+1
            self.session_usr.rollback()
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        else:
            return None

    #获取权限类别
    #param user:用户
    def get_role_type(self,user):
        userrole = self.get_role(user)
        rs = self.session_usr.query(Role).all()
        self.session_usr.rollback()
        roles=[]
        for item in rs:
            tmpItem={}
            role = item.role_basic.split(',')
            contain=True
            for roleitem in role:
                if roleitem in userrole:
                    continue
                else:
                    contain = False
            if contain:
                tmpItem['role_id'] = item.role_id
                tmpItem['role_name']=item.role_name
                roles.append(tmpItem)
        return json.dumps(roles)

    #获取所有用户所在部门信息
    #param user:用户信息
    #返回用户所在部门
    def get_role_department(self,user):
        roles = self.get_role(user)
        sql = 'select user_department from user group by user_department;'
        if '4' in roles and '5' not in roles and '6' not in roles:
            ret = []
            item = {}
            item['department'] = user.user_department
            ret.append(item)
            return json.dumps(ret)
        elif '5' in roles or '6' in roles:
            rs = self.session_usr.execute(sql).fetchall()
            self.session_usr.rollback()
            ret = []
            for i in rs:
                item = {}
                item['department'] = i[0]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    #获取所有用户所在班组信息
    #param user:用户信息
    #返回用户所在班组
    def get_role_team(self,user):
        roles = self.get_role(user)
        sql = 'select user_team from user group by user_team;'
        if '4' in roles and '5' not in roles and '6' not in roles:
            ret = []
            item = {}
            item['team'] = user.user_team
            ret.append(item)
            return json.dumps(ret)
        elif '5' in roles or '6' in roles:
            rs = self.session_usr.execute(sql).fetchall()
            self.session_usr.rollback()
            ret = []
            for i in rs:
                item = {}
                item['team'] = i[0]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    #获取所有班组信息
    #返回班组列表
    def get_role_teams(self):
        sql = 'select user_team from user group by user_team;'
        rs = self.session_usr.execute(sql).fetchall()
        self.session_usr.rollback()
        ret = []
        for i in rs:
            item = {}
            item['team'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #返回用户所在班组的班组管理员信息
    #param user:输入登录用户
    #返回用户所在班组的班组管理员姓名
    def get_teamManager(self,user):
        managers=self.session_usr.query(User.user_id).filter(User.user_team==user.user_team,User.user_role==4).all()
        ret = []
        for i in managers:
            item = {}
            item['team_manager'] = i.user_name
            ret.append(item)
        return  ret

    #获取当前登录用户所在班组信息
    #如果当前登录用户是班组管理员则展示本班组用户
    #如果当前登录用户是部门管理员则展示本部门用户
    #如果当前登录用户是总管理员则展示所有用户
    #param loginuser:当前登录的用户信息
    #返回用户
    def get_teamUser(self,loginuser):
        teamusers=[]
        if loginuser.user_role == 3:
            teamusers=self.session_usr.query(User).filter(User.user_department==loginuser.user_department,User.user_team==loginuser.user_team).all()
        elif loginuser.user_role == 4:
            teamusers=self.session_usr.query(User).filter(User.user_department==loginuser.user_department).all()
        elif loginuser.user_role == 5:
            teamusers=self.session_usr.query(User).all()
        else:
            return 1011501
        #解析用户名称
        rs_teamUsers=[]
        for item in teamusers:
            tmp={}
            tmp['username']=item.user_name
            rs_teamUsers.append(tmp)
        return rs_teamUsers

#无人机设备对象操作类
#包括设备查询，分页查询，条件查询，设备各种条件的统计以及设备的添加修改和删除功能
#author:Wu Wei
#Version 1.0.0.0
#所有错误代码以0201XXXX开始
class DeviceDAO:
    def __init__(self):
        self.session_uav = Session_UAV()

    def __del__(self):
        self.session_uav.close()

    #简单的设置成只能查看本部门的设备，根据用户进行查询，简单的设置为本部门的用户只能够查看本部门的所有设备
    #param user:当前登录的用户
    #返回所有无人机设备
    #author: Wu Wei P.S. 函数实用性较差已经弃用
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        rs=self.session_uav.query(Device).filter(Device.device_use_dpartment==user.user_department).all()
        self.session_uav.rollback()
        return class_to_dict(rs)

    #分页查询，查询用户所在部门的设备
    #param user:当前登录的用户信息
    #param page_index 查询第几页
    #param page_size 每一页展示的数据条数
    #返回查询到的所有设备
    # author: Wu Wei P.S. 函数实用性较差已经弃用
    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        rs=self.session_uav.query(Device).filter(Device.device_use_dpartment==user.user_department).limit(page_size).offset((page_index-1)*page_size).all()
        return class_to_dict(rs)

    #查询所有设备的页数
    #param user:用户信息
    #param device_type:设备类型为空则显示所有设备
    #param device_status:设备状态，为空则查询所有状态的设备
    #param page_size:每页展示的数据条数
    #返回页数json数据
    #修改查询权限 wuwei 2018-08-16
    def query_pages(self,user,device_type,device_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = self.session_uav.query(Device)

        #修改查询权限
        if '1' not in roles:
            return None
        if user.user_role<=4:
            q = q.filter(Device.device_use_dpartment == user.user_department)
        if user.user_role<=3:
            q=q.filter(Device.user_team==user.user_team)

        if device_type:
            q = q.filter(Device.device_type == device_type)
        if device_status:
            q = q.filter(Device.device_status == device_status)
        rs = q.count()/page_size+1
        self.session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    #根据设备id查看设备
    #param uav_id:输入无人机设备id
    #返回无人机设备
    def query_index(self,uav_id):
        return class_to_dict(self.session_uav.query(Device).filter(Device.device_id==uav_id).first())

    #条件查询，此查询包含各种条件以及分页查询，因此可以将分页查询废弃（所有查询记录都通过调用此函数实现）
    # 查看本部门的的设备（输电一所和输电二所）
    #param user:登录的用户信息
    #param device_id:无人机id
    #param device_ver:无人机类型
    #param device_type:无人机种类
    #param uad_code:无人机设备编码（已经改为民航局编码）
    #param device_status:无人机状态
    #param page_index:查询第几页
    #param page_size:每页展示数据条数
    #返回查询到的数据条数
    #修改查询权限 wuwei 2018-08-16
    def query_condition(self,user,device_id,device_ver,device_type,uad_code,device_status,page_index,page_size):
        q = self.session_uav.query(Device)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None
        if user.user_role<=4:
            q = q.filter(Device.device_use_dpartment == user.user_department)
        if user.user_role<=3:
            q=q.filter(Device.user_team==user.user_team)

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
        self.session_uav.rollback()
        return  class_to_dict(device)

    #统计用户所在输电所的设备情况
    #param user:用户信息
    #param device_status:设备状态
    #返回设备类型以及每类设备数目
    def query_statistic(self,user,device_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        sql=''
        if(device_status!='总数'):
            sql='select device_type,count(device_type) from tb_device where device_use_dpartment=\''+user.user_department+'\'&& device_status=\''+device_status+'\' group by device_type;'
        else:
            sql = 'select device_type,count(device_type) from tb_device where device_use_dpartment=\'' + user.user_department + '\' group by device_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['name']=i[0]
            item['value']=i[1]
            ret.append(item)
        return json.dumps(ret)

    #统计每一类设备情况
    #param user 当前登录用户
    #返回每一类设备各个状态的设备数目
    def query_statistic_all(self,user):
        #get type first
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        sql = 'select device_type from tb_device where device_use_dpartment=\'' + user.user_department + '\' group by device_type;'
        rs = self.session_uav.execute(sql).fetchall()
        self.session_uav.rollback()
        ret=[]
        if user.user_role<=4:
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_use_dpartment==user.user_department).all())
                item['instock']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='在库',Device.device_use_dpartment==user.user_department).all())
                item['removal'] = len(self.session_uav.query(Device).filter(Device.device_type == strType, Device.device_status == '出库',Device.device_use_dpartment==user.user_department).all())
                item['maintain']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='维修',Device.device_use_dpartment==user.user_department).all())
                item['scrap'] = len(self.session_uav.query(Device).filter(Device.device_type == strType, Device.device_status == '报废',Device.device_use_dpartment==user.user_department).all())
                item['lost']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='丢失',Device.device_use_dpartment==user.user_department).all())
                ret.append(item)
        else:
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(self.session_uav.query(Device).filter(Device.device_type==strType).all())
                item['instock']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='在库').all())
                item['removal'] = len(self.session_uav.query(Device).filter(Device.device_type == strType, Device.device_status == '出库').all())
                item['maintain']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='维修').all())
                item['scrap'] = len(self.session_uav.query(Device).filter(Device.device_type == strType, Device.device_status == '报废').all())
                item['lost']=len(self.session_uav.query(Device).filter(Device.device_type==strType,Device.device_status=='丢失').all())
                ret.append(item)
        return json.dumps(ret)

    #获取设备类型和设备型号
    #param user_team:查询某一班组的设备类型
    #返回设备类型的json数据
    def query_type(self,user_team):
        sql = 'select device_type from tb_device group by device_type;'
        rs = self.session_uav.execute(sql).fetchall()
        self.session_uav.rollback()
        ret = []
        for i in rs:
            item = {}
            item['device_type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #查询所有设备版本
    #返回设备备版本的json数据
    def query_ver(self):
        sql = 'select device_ver from tb_device group by device_ver;'
        rs = self.session_uav.execute(sql).fetchall()
        self.session_uav.rollback()
        ret = []
        for i in rs:
            item = {}
            item['device_ver'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #查询所有设备类型
    # 返回设备类型的json数据
    def query_type(self):
        sql = 'select device_type from tb_device group by device_type;'
        rs = self.session_uav.execute(sql).fetchall()
        self.session_uav.rollback()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #添加无人机设备
    #param usr:当前登录的用户信息
    #param device:需要添加的设备
    #添加成功返回1，返回其他值则添加失败
    def add_device(self,usr,device):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            #首先判断无人机是否存在
            exist = self.session_uav.query(Device).filter(Device.device_id==device.device_id).first()
            if exist is not None:
                return 2011101
            #不存在则添加
            self.session_uav.add(device)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2011102

    #修改无人机设备状态
    #param usr:当前登录用户信息
    #param device:修改后写回的设备
    def modify_device(self,usr,device):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        #判断是否有权限修改无人机
        if '3' in roles:
            uav=self.session_uav.query(Device).filter(Device.device_id == device.device_id).first()

            #无人机不存在
            if uav is None:
                return  2011201

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
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 02011202

    #修改无人机设备状态
    #状态有五种 在库 出库 维修 报废 丢失
    #param usr:当前登录用户信息
    #param device_id:无人机设备id
    #param status:修改后无人机状态
    def modify_device_status(self,usr,device_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            uav=self.session_uav.query(Device).filter(Device.device_id == device_id).first()
            uav.device_status=status
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 02011301

#电池设备对象操作类
#包括设备查询，分页查询，条件查询，设备各种条件的统计以及设备的添加修改和删除功能
#author:Wu Wei
#Version 1.0.0.0
#所有错误代码以0202XXXX开始
class BatteryDAO:
    def __init__(self):
        self.session_uav = Session_UAV()

    def __del__(self):
        self.session_uav.close()

    #查询用户所在部门所有设备
    #param usr:登录用户
    #返回获取的所有设备 P.S. 弃用 通过条件查询替代
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        rs=self.session_uav.query(Battery).filter(Battery.battery_use_dpartment==user.user_department).all()
        self.session_uav.rollback()
        return class_to_dict(rs)

    #分页查询所有设备
    #param user:当前登录用户
    #param page_index: 当前展示的页数
    #param page_size: 每一页展示数据条数
    #返回获取的设备 P.S. 弃用，通过条件查询替代
    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        rs=self.session_uav.query(Battery).filter(Battery.battery_use_dpartment==user.user_department).limit(page_size).offset((page_index-1)*page_size).all()
        return class_to_dict(rs)

    #获取设备页数
    #param user:当前登录用户
    #param battery_type:电池类型
    #param battery_status 电池状态
    #param page_size 每一页展示数据的条数
    #返回查询设备总页数
    #修改查询权限 wuwei 2018-08-16
    def query_pages(self,user,battery_type,battery_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = self.session_uav.query(Battery)
        if '1' not in roles:
            return None
        # 修改查询权限
        if user.user_role<=4:
            q = q.filter(Battery.battery_use_dpartment == user.user_department)
        if user.user_role<=3:
            q = q.filter(Battery.user_team == user.user_team)
        if battery_type:
            q = q.filter(Battery.battery_type == battery_type)
        if battery_status:
            q = q.filter(Battery.battery_status == battery_status)
        rs = q.count()/page_size+1
        self.session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    #根据条件进行分页查询
    #param user:当前登录的用户
    #param battery_id:电池id
    #param battery_ver:电池版本
    #param battery_type:电池类型
    #param battery_status:电池状态
    #param page_index:展示第几页的数据
    #param page_size:每一页展示数据条数
    #返回查询设备
    #修改查询权限 wuwei 2018-08-16
    def query_condition(self,user,bttery_id,bttery_ver,bttery_type,bttery_status,page_index,page_size):
        q = self.session_uav.query(Battery)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None
        # 修改查询权限
        if user.user_role<=4:
            q = q.filter(Battery.battery_use_dpartment == user.user_department)
        if user.user_role<=3:
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
        self.session_uav.rollback()
        return class_to_dict(battery)

    #查询统计信息
    #查询不同类型的电池的数目
    #param user:当前登录用户
    #param battery_status:电池状态（输入’总数‘，统计所有状态）
    #返回统计结果
    def query_statistic(self,user,bttery_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        sql=''
        if(bttery_status!='总数'):
            sql='select battery_type,count(battery_type) from tb_battery where battery_use_dpartment=\''+user.user_department+'\'&& battery_status=\''+bttery_status+'\' group by battery_type;'
        else:
            sql = 'select battery_type,count(battery_type) from tb_battery where battery_use_dpartment=\'' + user.user_department + '\' group by battery_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['name']=i[0]
            item['value']=i[1]
            ret.append(item)
        return json.dumps(ret)

    #统计不同类型不同状态下的电池的统计结果
    #param user:当前登录用户
    #返回统计结果
    def query_statistic_all(self,user):
        #get type first
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        sql = 'select battery_type from tb_battery where battery_use_dpartment=\'' + user.user_department + '\' group by battery_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret=[]
        if user.user_role<=4:
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_use_dpartment==user.user_department).all())
                item['instock']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='在库',Battery.battery_use_dpartment==user.user_department).all())
                item['removal']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='出库',Battery.battery_use_dpartment==user.user_department).all())
                item['maintain']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='维修',Battery.battery_use_dpartment==user.user_department).all())
                item['scrap']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='报废',Battery.battery_use_dpartment==user.user_department).all())
                item['lost'] = len(self.session_uav.query(Battery).filter(Battery.battery_type == strType, Battery.battery_status == '丢失',Battery.battery_use_dpartment==user.user_department).all())
                ret.append(item)
        else:
            for idx in rs:
                item = {}
                strType=idx[0]
                item['name']=strType
                item['count']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType).all())
                item['instock']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='在库').all())
                item['removal']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='出库').all())
                item['maintain']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='维修').all())
                item['scrap']=len(self.session_uav.query(Battery).filter(Battery.battery_type==strType,Battery.battery_status=='报废').all())
                item['lost'] = len(self.session_uav.query(Battery).filter(Battery.battery_type == strType, Battery.battery_status == '丢失').all())
                ret.append(item)
        return json.dumps(ret)

    #查询电池类型
    #param user_team:用户所在班组
    #查询本班组所有电池类型
    def query_type(self,user_team):
        sql = 'select battery_type from tb_battery where user_team=\'' + user_team + '\' group by battery_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['battery_type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #查询所有电池类型
    #返回所有电池类型
    def query_type(self):
        sql = 'select battery_type from tb_battery group by battery_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #添加电池（将电池添加进入到电池数据表中）
    #param usr:当前登录用户
    #param battery:待添加的电池
    def add_battery(self,usr,battery):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            #首先判断是否存在
            exist = self.session_uav.query(Battery).filter(Battery.battery_id==battery.battery_id).first()
            if exist is not None:
                return 2020901

            self.session_uav.add(battery)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2020902

    #添加电池（将电池添加进入到电池数据表中）
    #param usr:当前登录用户
    #param battery:修改后的电池数据
    def modify_battery(self,usr,battery):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            batteryobj=self.session_uav.query(Battery).filter(Battery.battery_id == battery.battery_id).first()
            if batteryobj is None:
                return 2021001

            batteryobj.battery_ver = battery.battery_ver
            batteryobj.battery_type = battery.battery_type
            batteryobj.battery_fact = battery.battery_fact
            batteryobj.battery_date = battery.battery_date
            batteryobj.user_team = battery.user_team
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2021002

    #修改电池状态
    #param usr:当前登录用户
    #param battery_id:电池id
    #param status:修改后电池状态
    def modify_battery_status(self,usr,battery_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            battery=self.session_uav.query(Battery).filter(Battery.battery_id==battery_id).first()
            battery.battery_status=status
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2021101

#平板设备对象操作类
#包括设备查询，分页查询，条件查询，设备各种条件的统计以及设备的添加修改和删除功能
#author:Wu Wei
#Version 1.0.0.0
#所有错误代码以0203XXXX开始
class PadDao:
    def __init__(self):
        self.session_uav = Session_UAV()

    def __del__(self):
        self.session_uav.close()

    # 查询所有平板设备
    # param user: 当前登录用户信息
    #返回查询到的结果数据
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=self.session_uav.query(Pad).filter(Pad.user_team==user.user_team).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = self.session_uav.query(Pad).all()
            return class_to_dict(rs)
        else:
            return None

    #分页查询
    #param user:当前登录用户
    #param page_index:当前显示的数据页
    #param page_size:每页显示数据条数
    #返回查询结果
    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=self.session_uav.query(Pad).filter(Pad.user_team==user.user_team).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = self.session_uav.query(Pad).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    #查询总页数
    #param user:当前登录的用户
    #param pad_type:查询平台类型
    #param pad_status:查询平板状态
    #param page_size:每一页展示数据条数
    #返回查询总页数
    #修改查询权限 wuwei 2018-08-16
    def query_pages(self,user,pad_type,pad_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = self.session_uav.query(Pad)
        roles=usrDao.get_role(user)

        #修改查询权限 wuwei
        if '1' not in roles:
            return None
        if user.user_role<=4:
            q = q.filter(Pad.pad_use_dpartment == user.user_department)
        if user.user_role<=3:
            q = q.filter(Pad.user_team == user.user_team)

        if pad_type:
            q = q.filter(Pad.pad_type == pad_type)
        if pad_status:
            q = q.filter(Pad.pad_status == pad_status)
        rs = q.count()/page_size+1
        self.session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    #条件查询，根据输入条件对平板设备进行分页查询
    #param user:登录的用户
    #param pad_id:平板id
    #param pad_ver:平板版本
    #param pad_type:平板类型
    #param pad_status:平板状态
    #param page_index:当前显示的页数
    #param page_size:每一页大小
    #修改查询权限 wuwei 2018-08-16
    def query_condition(self, user, pad_id, pad_ver, pad_type, pad_status, page_index, page_size):
        q = self.session_uav.query(Pad)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None

        #修改查询权限 wuwei
        if user.user_role<=4:
            q = q.filter(Pad.pad_use_dpartment == user.user_department)
        if user.user_role<=3:
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

    #查询统计信息
    #param user:当前登录用户
    #param pad_status:平板状态
    #返回查询结果
    def query_statistic(self,user,pad_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            sql=''
            if(pad_status!='总数'):
                sql='select pad_type,count(pad_type) from tb_pad where user_team=\''+user.user_team+'\'&& pad_status=\''+pad_status+'\' group by pad_type;'
            else:
                sql = 'select pad_type,count(pad_type) from tb_pad where user_team=\'' + user.user_team + '\' group by pad_type;'
            rs = self.session_uav.execute(sql).fetchall()
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

            rs = self.session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    #查询平板类型信息 查询所有平板的类型信息
    #返回平板类型
    def query_type(self):
        sql = 'select pad_type from tb_pad group by pad_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #添加平板信息
    #param usr:当前登录用户
    #param pad:需要添加的平板
    def add_pad(self,usr,pad):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            existed = self.session_uav.query(Pad).filter(Pad.pad_id==pad.pad_id).first()
            #self.session_uav.rollback()
            if(existed is not None):
                return 2030701
            self.session_uav.add(pad)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2030702

    #修改平板信息
    #param usr:当前登录用户
    #param pad:需要修改的平板信息
    def modify_pad(self,usr,pad):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            padtmp=self.session_uav.query(Pad).filter(Pad.pad_id == pad.pad_id).first()
            padtmp.pad_ver = pad.pad_ver
            padtmp.pad_type = pad.pad_type
            padtmp.pad_fact = pad.pad_fact
            padtmp.pad_date = pad.pad_date
            padtmp.user_team = pad.user_team
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2030801

    #修改平板状态
    #param usr:当前登录的用户
    #param pad_id:修改修改的平板的id
    #param status:修改后平板状态
    def modify_pad_status(self,usr,pad_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            pad=self.session_uav.query(Pad).filter(Pad.pad_id == pad_id).first()
            pad.pad_status=status
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2030901


#配件设备对象操作类
#包括设备查询，分页查询，条件查询，设备各种条件的统计以及设备的添加修改和删除功能
#author:Wu Wei
#Version 1.0.0.0
#所有错误代码以0204XXXX开始
class PartsDao:
    def __init__(self):
        self.session_uav = Session_UAV()

    def __del__(self):
        self.session_uav.close()

    #查询所有配件设备
    #param user:输入的用户信息
    #返回所有配件数据
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            return class_to_dict(self.session_uav.query(Parts).all())
        else:
            return None

    #分页查询查询配件信息
    #param user:输入用户信息
    #param page_index:查询第几页
    #param page_size:查询每一页数据条数
    #返回所有配件数据
    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            rs=self.session_uav.query(Parts).filter(Parts.user_team==user.user_team).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs = self.session_uav.query(Parts).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    #查询配件页数
    #param usr:当前登录用户
    #param parts_type:配件类型
    #param parts_status:配件状态
    #param page_size:每一页展示数据数量
    #返回所有配件数据
    #修改查询权限
    def query_pages(self,user,parts_type,parts_status,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = self.session_uav.query(Parts)
        if '1' not in roles:
            return None
        # 修改查询权限 wuwei
        if user.user_role<=4:
            q = q.filter(Parts.parts_use_dpartment == user.user_department)
        if user.user_role<=3:
            q = q.filter(Parts.user_team == user.user_team)
        if parts_type:
            q = q.filter(Parts.parts_type == parts_type)
        if parts_status:
            q = q.filter(Parts.parts_status == parts_status)
        rs = q.count()/page_size+1
        self.session_uav.rollback()
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    #查询配件的统计信息
    #param user:当前登录用户
    #param part_status:配件状态
    def query_statistic(self,user,part_status):
        usrDao=UserDAO()
        roles = usrDao.get_role(user)
        if user.user_role<=4:
            sql=''
            if(part_status!='总数'):
                sql='select parts_type,count(parts_type) from tb_parts where user_department=\''+user.user_department+'\'&& parts_status=\''+part_status+'\' group by parts_type;'
            else:
                sql = 'select parts_type,count(parts_type) from tb_parts where user_department=\'' + user.user_department + '\' group by parts_type;'
            rs = self.session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        elif user.user_role>=5:
            sql=''
            if(part_status!='总数'):
                sql='select parts_type, count(parts_type) from tb_parts where parts_status=\''+part_status+'\' group by parts_type;'
            else:
                sql = 'select parts_type, count(parts_type) from tb_parts group by parts_type;'
            rs = self.session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    #查询配件信息
    #param user:当前登录用户
    #param part_status:配件状态
    def query_type(self):
        sql = 'select parts_type from tb_parts group by parts_type;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['type'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #条件查询
    #param user:当前登录用户
    #param parts_id:配件di
    #param parts_ver:配件类型
    #param parts_status:配件状态
    #param page_index:当前显示页
    #param page_size:每页展示数据条数
    #修改查询权限 wuwei 2018-08-16
    def query_condition(self,user,parts_id,parts_ver,parts_type,parts_status,page_index,page_size):
        q = self.session_uav.query(Parts)
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' not in roles:
            return None
        # 修改查询权限 wuwei
        if user.user_role<=4:
            q = q.filter(Parts.parts_use_dpartment == user.user_department)
        if user.user_role<=3:
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

    #添加部件
    #param usr;登录的用户信息
    #param parts:待添加的配件
    def add_parts(self,usr,parts):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '2' in roles:
            exist = self.session_uav.query(Parts).filter(Parts.parts_id==parts.parts_id).first()
            if exist is not None:
                return 2030701

            self.session_uav.add(parts)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2030702

    #修改部件
    #param usr:当前登录的用户
    #param parts:修改后的配件
    def modify_parts(self,usr,parts):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            partstmp=self.session_uav.query(Parts).filter(Parts.parts_id==parts.parts_id).first()
            if partstmp is None:
                return 2030801

            partstmp.parts_ver = parts.parts_ver
            partstmp.parts_type = parts.parts_type
            partstmp.parts_fact = parts.parts_fact
            partstmp.parts_date = parts.parts_date
            partstmp.user_team = parts.user_team
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2030802

    #修改配件状态
    #param usr:当前登录的用户
    #param parts_id:配件id
    #param status:配件状态
    def modify_parts_status(self,usr,parts_id,status):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        if '3' in roles:
            parts=self.session_uav.query(Parts).filter(Parts.parts_id==parts_id).first()
            parts.parts_status=status
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2030901

#出入库管理
#出入库管理功能比较复杂
# 涉及到设备的出入库,设备借调以及设备申请 而且由于每个设备都通过一张表来保存
# 所以查询和修改的时候也相对比较复杂，感觉数据表结构需要进行调整才行
# 根据现在的经验来看实际上所有的设备都可以放在一张表中，避免查询的时候过多的判断，这个在后面三个月需要进行仔细思考后进行修改
#author: Wu Wei
#Version 1.0.0.0
#所有错误代码以0205XXXX开始
class ManagerDAO:
    def __init__(self):
        self.session_uav = Session_UAV()
        self.session_usr = Session_User()
    def __del__(self):
        self.session_uav.close()
        self.session_usr.close()

    #查询所有出入库管理记录
    #param user:当前登录的用户信息
    def query_all(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            return class_to_dict(self.session_uav.query(Manager).all())
        else:
            return None

    #分页查询借用记录
    #param user:当前登录的用户的信息
    #param page_index:数据显示的当前页
    #param page_size:数据显示每一页数据展示条数
    def query_page(self,user,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            q=self.session_uav.query(Manager)
            return class_to_dict(self.session_uav.query(Manager).limit(page_size).offset((page_index-1)*page_size).all())
        else:
            return None

    #根据时间段对借用记录进行查询
    #param user:当前登录的用户的信息
    #param page_index:数据显示的当前页
    #param page_size:数据显示每一页数据展示条数
    #param sttime:起始时间
    #param endtime:结束时间
    def query_time(self,user,page_index,page_size,sttime,endtime):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            q = self.session_uav.query(Manager)
            rs = q.filter(Manager.borrow_date.between(sttime,endtime)).limit(page_size).offset((page_index-1)*page_size).all()
            return class_to_dict(rs)
        else:
            return None

    #查询历史记录的页数
    #param user:当前登录用户信息
    #param page_size:每页展示数据条数
    def query_history_pagenumber(self,user,page_size):
        rs=self.session_uav.query(Manager).count()/page_size+1
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    #根据日期查询页数
    #param user:当前登录的用户信息
    #param page_size:每页展示数据条数
    #param sttime:起始时间
    #param endtime:终止时间
    def query_date_pagenumber(self,user,page_size,sttime,endtime):
        q = self.session_uav.query(Manager)
        rs = q.filter(Manager.borrow_date.between(sttime, endtime)).count()/page_size+1
        item = {}
        item['pages'] = rs
        return json.dumps(item)

    #设备的库存状态查询，由于每类设备对应一张数据表，所以每个设备对应一个函数进行查询，在查询的过程中有众多的条件判断需要处理
    #param device_type:设备类型
    #param device_status:设备状态
    #param page_index:当前显示页
    #param page_size:每页显示的条数
    def query_uav_manager(self,device_type,device_status,page_index,page_size):
        ret = []
        q = self.session_uav.query(Device)
        if device_type is not None:
            q = q.filter(Device.device_type == device_type)
        if device_status is not None:
            q = q.filter(Device.device_status == device_status)
        devices = q.limit(page_size).offset((page_index - 1) * page_size).all()
        self.session_uav.rollback()
        for item in devices:
            tmp = {}
            if item.device_status == '出库':
                mnger = self.session_uav.query(Manager).filter(Manager.device_id == item.device_id,
                                                               Manager.manager_status == '借用').first()
                tmp['device_ver'] = item.device_ver
                tmp['device_type'] = item.device_type
                tmp['device_id'] = item.device_id
                tmp['user_team'] = item.user_team
                if mnger is not None:
                    tmp['borrow_team'] = mnger.user_team
                    tmp['borrower'] = mnger.borrower_name
                    tmp['status'] = '出库'
                else:
                    tmp['borrow_team'] = ''
                    tmp['borrower'] = ''
                    tmp['status'] = '出库'
                ret.append(tmp)
            elif item.device_status == '维修':
                tmp['device_ver'] = item.device_ver
                tmp['device_type'] = item.device_type
                tmp['device_id'] = item.device_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '维修'
                ret.append(tmp)
            elif item.device_status == '报废':
                tmp['device_ver'] = item.device_ver
                tmp['device_type'] = item.device_type
                tmp['device_id'] = item.device_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '报废'
                ret.append(tmp)
            elif item.device_status == '丢失':
                tmp['device_ver'] = item.device_ver
                tmp['device_type'] = item.device_type
                tmp['device_id'] = item.device_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '丢失'
                ret.append(tmp)
            else:
                tmp['device_ver'] = item.device_ver
                tmp['device_type'] = item.device_type
                tmp['device_id'] = item.device_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '在库'
                ret.append(tmp)
        return ret
    def query_battery_manager(self,device_type,device_status,page_index,page_size):
        ret=[]
        q = self.session_uav.query(Battery)
        if device_type is not None:
            q = q.filter(Battery.battery_type == device_type)
        if device_status is not None:
            q = q.filter(Battery.battery_status == device_status)
        batteries = q.limit(page_size).offset((page_index - 1) * page_size).all()
        self.session_uav.rollback()
        for item in batteries:
            tmp = {}
            if item.battery_status == '出库':
                mnger = self.session_uav.query(Manager).filter(Manager.device_id == item.battery_id,
                                                               Manager.manager_status == '借用').first()
                tmp['device_ver'] = item.battery_ver
                tmp['device_type'] = item.battery_type
                tmp['device_id'] = item.battery_id
                tmp['user_team'] = item.user_team

                if mnger is not None:
                    tmp['borrow_team'] = mnger.user_team
                    tmp['borrower'] = mnger.borrower_name
                    tmp['status'] = '出库'
                else:
                    tmp['borrow_team'] = ''
                    tmp['borrower'] = ''
                    tmp['status'] = '出库'
                ret.append(tmp)
            else:
                tmp['device_ver'] = item.battery_ver
                tmp['device_type'] = item.battery_type
                tmp['device_id'] = item.battery_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '在库'
                ret.append(tmp)
        return ret
    def query_parts_manager(self,device_type,device_status,page_index,page_size):
        ret=[]
        q = self.session_uav.query(Parts)
        if device_type is not None:
            q = q.filter(Parts.parts_type == device_type)
        if device_status is not None:
            q = q.filter(Parts.parts_status == device_status)
        parts = q.limit(page_size).offset((page_index - 1) * page_size).all()
        self.session_uav.rollback()
        for item in parts:
            tmp = {}
            if item.parts_status == '出库':
                mnger = self.session_uav.query(Manager).filter(Manager.device_id == item.parts_id,
                                                               Manager.manager_status == '借用').first()
                tmp['device_ver'] = item.parts_ver
                tmp['device_type'] = item.parts_type
                tmp['device_id'] = item.parts_id
                tmp['user_team'] = item.user_team
                if mnger is not None:
                    tmp['borrow_team'] = mnger.user_team
                    tmp['borrower'] = mnger.borrower_name
                    tmp['status'] = '出库'
                else:
                    tmp['borrow_team'] = ''
                    tmp['borrower'] = ''
                    tmp['status'] = '出库'
                ret.append(tmp)
            else:
                tmp['device_ver'] = item.parts_ver
                tmp['device_type'] = item.parts_type
                tmp['device_id'] = item.parts_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '在库'
                ret.append(tmp)
        return ret
    def query_pads_manager(self,device_type,device_status,page_index,page_size):
        ret=[]
        q = self.session_uav.query(Pad)
        if device_type is not None:
            q = q.filter(Pad.pad_type == device_type)
        if device_status is not None:
            q = q.filter(Pad.pad_status == device_status)
        pads = q.limit(page_size).offset((page_index - 1) * page_size).all()
        self.session_uav.rollback()
        for item in pads:
            tmp = {}
            if item.pad_status == '出库':
                mnger = self.session_uav.query(Manager).filter(Manager.device_id == item.pad_id,
                                                               Manager.manager_status == '借用').first()
                tmp['device_ver'] = item.pad_ver
                tmp['device_type'] = item.pad_type
                tmp['device_id'] = item.pad_id
                tmp['user_team'] = item.user_team
                if mnger is not None:
                    tmp['borrow_team'] = mnger.user_team
                    tmp['borrower'] = mnger.borrower_name
                    tmp['status'] = '出库'
                else:
                    tmp['borrow_team'] = ''
                    tmp['borrower'] = ''
                    tmp['status'] = '出库'
                ret.append(tmp)
            else:
                tmp['device_ver'] = item.pad_ver
                tmp['device_type'] = item.pad_type
                tmp['device_id'] = item.pad_id
                tmp['user_team'] = item.user_team
                tmp['borrow_team'] = ''
                tmp['borrower'] = ''
                tmp['status'] = '在库'
                ret.append(tmp)
        return ret
    def query_device_manager(self,device_type,device_ver,device_status,page_index,page_size):
        ret = []
        if device_ver=='无人机':
            ret = self.query_uav_manager(device_type,device_status,page_index,page_size)
        elif device_ver=='电池':
            ret = self.query_battery_manager(device_type,device_status,page_index,page_size)
        elif device_ver=="配件":
            ret = self.query_parts_manager(device_type,device_status,page_index,page_size)
        elif device_ver=="平板":
            ret = self.query_pads_manager(device_type,device_status,page_index,page_size)
        return json.dumps(ret)

    #直接根据设备情况查询页数
    #param user:用户信息
    #param device_type:设备类型
    #param device_ver:设备种类
    #param device_status:设备状态
    #param page_size:每页展示数据条数
    def query_pages(self,user,device_type,device_ver,device_status,page_size):
        if device_ver=='无人机':
            q=self.session_uav.query(Device)
            if device_type is not None:
                q =q.filter(Device.device_type==device_type)
            if device_status is not None:
                q =q.filter(Device.device_status==device_status)
            rs= q.count()/page_size+1
            self.session_uav.rollback()
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        elif device_ver=='电池':
            q=self.session_uav.query(Battery)
            if device_type is not None:
                q =q.filter(Battery.battery_type==device_type)
            if device_status is not None:
                q =q.filter(Battery.battery_status==device_status)
            rs= q.count()/page_size+1
            self.session_uav.rollback()
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        elif device_ver=="配件":
            q=self.session_uav.query(Parts)
            if device_type is not None:
                q =q.filter(Parts.parts_type==device_type)
            if device_status is not None:
                q =q.filter(Parts.parts_status==device_status)
            rs= q.count()/page_size+1
            self.session_uav.rollback()
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        elif device_ver=="平板":
            q=self.session_uav.query(Pad)
            if device_type is not None:
                q =q.filter(Pad.pad_type==device_type)
            if device_status is not None:
                q =q.filter(Pad.pad_status==device_status)
            rs= q.count()/page_size+1
            self.session_uav.rollback()
            item = {}
            item['pages'] = rs
            return json.dumps(item)

    #查询设备借用情况（只能看到本班组的设备的借用情况，实际上由于展示策略的问题已经弃用）
    #param user:当前登录的用户
    def query_borrow(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        #只能看到本班组设备的借用情况
        if '1' in roles:
            return class_to_dict(self.session_uav.query(Manager).filter(Manager.manager_status=='借用',Manager.user_team==user.user_team).all())
        elif '5' in roles:
            return class_to_dict(self.session_uav.query(Manager).filter(Manager.manager_status == '借用',
                                                                        Manager.device_department == user.user_department).all())
        else:
            return None

    #条件查询，根据条件查询借用记录
    #param user:当前登录的用户信息
    #param device_ver:设备种类
    #param device_id:设备id
    #param device_type:设备类型
    #param manager_status:设备管理状态
    #param borrow_time:设备借用时间
    #param return_time:设备归还时间
    #param page_index:当前展示的页数
    #param page_size:每页展示的数据条数
    def query_condition(self,user,device_ver,device_id,device_type,manager_status,borrow_time,return_time,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles:
            q = self.session_uav.query(Manager)
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
    #   代码需要优化

    #   代码优化 2018.07.05
    #   Author   Frank. Wu
    #直接更新借用信息
    def updateManager(self,borrower,borrow_team,device,borrow_time,return_time,idx):
        if idx==1:
            obj = Manager(device_id=device.device_id, device_ver=device.device_ver, device_type=device.device_type,
                          borrower_name=borrower.user_id, borrow_date=borrow_time,user_team=borrow_team,
                          manager_status='借用', return_date=return_time)
            self.session_uav.add(obj)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            self.session_uav.query(Device).filter(Device.device_id == device.device_id).update(
                {Device.device_status: '出库', Device.device_use_number: device.device_use_number + 1},
                synchronize_session=False)
        if idx==2:
            obj = Manager(device_id=device.battery_id, device_ver=device.battery_ver, device_type=device.battery_type,
                          borrower_name=borrower.user_id, borrow_date=borrow_time,user_team=borrow_team,
                          manager_status='借用', return_date=return_time)
            self.session_uav.add(obj)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            self.session_uav.query(Battery).filter(Battery.battery_id == device.battery_id).update(
                {Battery.battery_status: '出库', Battery.battery_use_number: device.battery_use_number + 1},
                synchronize_session=False)
        if idx==3:
            obj = Manager(device_id=device.parts_id, device_ver=device.parts_ver, device_type=device.parts_type,
                          borrower_name=borrower.user_id, borrow_date=borrow_time,
                          user_team=borrow_team, manager_status='借用', return_date=return_time)
            self.session_uav.add(obj)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            self.session_uav.query(Parts).filter(Parts.parts_id == device.parts_id).update(
                {Parts.parts_status: '出库', Parts.parts_use_number: device.parts_use_number + 1},
                synchronize_session=False)
        if idx==4:
            obj = Manager(device_id=device.pad_id, device_ver=device.pad_ver, device_type=device.pad_type,
                          borrower_name=borrower.user_id, borrow_date=borrow_time,
                          user_team=borrow_team, manager_status='借用', return_date=return_time)
            self.session_uav.add(obj)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            self.session_uav.query(Pad).filter(Pad.pad_id == device.pad_id).update(
                {Pad.pad_status: '出库', Pad.pad_use_number: device.pad_use_number + 1},
                synchronize_session=False)
        try:
            self.session_uav.commit()
        except:
            self.session_uav.rollback()
        return 1
    #同一个班组的借用
    def borrow_in_team(self,user,borrower,borrow_team,device,borrow_time,return_time,idx):
        #判断设备是否在库
        if idx==1 and device.device_status=='在库':
            return self.updateManager(borrower,borrow_team,device,borrow_time,return_time,idx)
        if idx == 2 and device.battery_status == '在库':
            return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
        if idx == 3 and device.parts_status == '在库':
            return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
        if idx == 4 and device.pad_status == '在库':
            return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
        return 2051501
    #不是同一个班组的借用
    def borrow_notin_team(self,user,borrower,borrow_team,device,borrow_time,return_time,idx):
        #判断是否提交借调申请
        approve = self.session_uav.query(Approval).filter(Approval.apply_person == user.user_name).first()

        if  approve != None and approve.approval_status==1: #通过审批则直接借用
            #判断借用的飞机和审批的飞机是不是同一班组或者是管理员
            userDao = UserDAO()
            approver = self.session_usr.query(User).filter(User.user_id==approve.approval_person).first()
            roles = userDao.get_role(approver)

            # 判断设备是否在库
            if idx == 1 and device.device_status == '在库':
                if ('5' in roles and device.device_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    approvalDao = ApprovalDao()
                    approvalDao.approval_finished(borrower.user_id)
                    return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
                else:
                    return 2051601
            if idx == 2 and device.battery_status == '在库':
                if ('5' in roles and device.battery_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    approvalDao = ApprovalDao()
                    approvalDao.approval_finished(borrower.user_id)
                    return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
                else:
                    return 2051602
            if idx == 3 and device.parts_status == '在库':
                if ('5' in roles and device.parts_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    approvalDao = ApprovalDao()
                    approvalDao.approval_finished(borrower.user_id)
                    return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
                else:
                    return 2051603
            if idx == 4 and device.pad_status == '在库':
                if ('5' in roles and device.pad_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    approvalDao = ApprovalDao()
                    approvalDao.approval_finished(borrower.user_id)
                    return self.updateManager(borrower, borrow_team, device, borrow_time, return_time, idx)
                else:
                    return 2051604
        return 2051605
    #同一个班组的借用列表
    def borrow_in_teamList(self,user,borrower,borrow_team,device,borrow_time,return_time,idx):
        #判断设备是否在库
        if idx==1 and device.device_status=='在库':
            return 1
        if idx == 2 and device.battery_status == '在库':
            return 1
        if idx == 3 and device.parts_status == '在库':
            return 1
        if idx == 4 and device.pad_status == '在库':
            return 1
        return 2051701
    #不是同一个班组的借用列表
    def borrow_notin_teamList(self,user,borrower,borrow_team,device,borrow_time,return_time,idx):
        #判断是否提交借调申请
        approve = self.session_uav.query(Approval).filter(Approval.apply_person == user.user_name).first()

        if  approve != None and approve.approval_status==1: #通过审批则直接借用
            #判断借用的飞机和审批的飞机是不是同一班组或者是管理员
            userDao = UserDAO()
            approver = self.session_usr.query(User).filter(User.user_id==approve.approval_person).first()
            roles = userDao.get_role(approver)

            # 判断设备是否在库
            if idx == 1 and device.device_status == '在库':
                if ('5' in roles and device.device_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    return 1
                else:
                    return 2051801
            if idx == 2 and device.battery_status == '在库':
                if ('5' in roles and device.battery_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    return 1
                else:
                    return 2051802
            if idx == 3 and device.parts_status == '在库':
                if ('5' in roles and device.parts_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    return 1
                else:
                    return 2051803
            if idx == 4 and device.pad_status == '在库':
                if ('5' in roles and device.pad_use_dpartment==approver.user_department) or\
                    ('4' in roles and device.user_team==approver.user_team):
                    return 1
                else:
                    return 2051804
        return 2051805


    #数据借用，确认借用直接写进数据库中
    #param user:登录用户
    #param borrower:借用人
    #param borrow_team:借用班组
    #param uav_id:设备id
    #param borrow_time:借用时间
    #param return:归还时间
    def manager_borrow(self,user,borrower,borrow_team,uav_id,borrow_time,return_time):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        #判断设备类型
        device = self.session_uav.query(Device).filter(Device.device_id == uav_id).first()
        battery = self.session_uav.query(Battery).filter(Battery.battery_id == uav_id).first()
        part = self.session_uav.query(Parts).filter(Parts.parts_id == uav_id).first()
        pad = self.session_uav.query(Pad).filter(Pad.pad_id == uav_id).first()
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
        if idx==0:
            return 2051901
        if status!='在库':
            return 2051902#设备未归还


        #判断是否是一个班组
        usr=self.session_usr.query(User).filter(User.user_name==borrower).first()
        self.session_usr.rollback()
        #如果用户不存在
        if usr==None:
            return 2051903

        #如果不是同一班组
        #userApprover = self.session_usr.query(User).filter(User.user_id==approver).first()
        if usr.user_team!=user_team:
            if idx==1:
                return self.borrow_notin_team(user,usr,usr.user_team,device,borrow_time,return_time,idx)
            if idx==2:
                return self.borrow_notin_team(user, usr, usr.user_team, battery, borrow_time, return_time,idx)
            if idx==3:
                return self.borrow_notin_team(user, usr, usr.user_team, part, borrow_time, return_time,idx)
            if idx==4:
                return self.borrow_notin_team(user, usr, usr.user_team, pad, borrow_time, return_time,idx)
        else:#同一班组
            if idx==1:
                return self.borrow_in_team(user,usr,usr.user_team,device,borrow_time,return_time,idx)
            if idx==2:
                return self.borrow_in_team(user, usr, usr.user_team, battery, borrow_time, return_time,idx)
            if idx==3:
                return self.borrow_in_team(user, usr, usr.user_team, part, borrow_time, return_time,idx)
            if idx==4:
                return self.borrow_in_team(user, usr, usr.user_team, pad, borrow_time, return_time,idx)

    #返回借用列表
    #param user:当前登录的用户信息
    #param borrowList:借用类表
    def manager_borrowList(self,user,borrowList):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        result = []
        idx = 0
        for borrowItem in borrowList:
            tmp={}
            device_id = borrowItem.device_id
            #判断设备类型
            device = self.session_uav.query(Device).filter(Device.device_id == device_id).first()
            battery = self.session_uav.query(Battery).filter(Battery.battery_id == device_id).first()
            part = self.session_uav.query(Parts).filter(Parts.parts_id == device_id).first()
            pad = self.session_uav.query(Pad).filter(Pad.pad_id == device_id).first()
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
            if idx==0:
                continue
            if status!='在库':
                continue

            borrower = borrowItem.borrower_name
            #判断是否是一个班组
            usr=self.session_usr.query(User).filter(User.user_name==borrower).first()
            self.session_usr.rollback()
            #如果用户不存在
            if usr==None:
                continue
            #如果不是同一班组
            #userApprover = self.session_usr.query(User).filter(User.user_id==approver).first()
            if usr.user_team!=user_team:
                if idx==1:
                    if self.borrow_notin_teamList(user,usr,usr.user_team,device,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        continue
                    else:
                        tmp['type']=device.device_type
                        tmp['id']=device.device_id
                        tmp['team']=device.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
                if idx==2:
                    if self.borrow_notin_teamList(user, usr, usr.user_team, battery,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=battery.battery_type
                        tmp['id']=battery.battery_id
                        tmp['team']=battery.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
                if idx==3:
                    if self.borrow_notin_teamList(user, usr, usr.user_team, part,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=part.parts_type
                        tmp['id']=part.parts_id
                        tmp['team']=part.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
                if idx==4:
                    if self.borrow_notin_teamList(user, usr, usr.user_team, pad,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=pad.pad_type
                        tmp['id']=pad.pad_id
                        tmp['team']=pad.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
            else:#同一班组
                if idx==1:
                    if self.borrow_in_teamList(user,usr,usr.user_team,device,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=device.device_type
                        tmp['id']=device.device_id
                        tmp['team']=device.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
                if idx==2:
                    if self.borrow_in_teamList(user, usr, usr.user_team, battery,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=battery.battery_type
                        tmp['id']=battery.battery_id
                        tmp['team']=battery.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
                if idx==3:
                    if self.borrow_in_teamList(user, usr, usr.user_team, part,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=part.parts_type
                        tmp['id']=part.parts_id
                        tmp['team']=part.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
                if idx==4:
                    if self.borrow_in_teamList(user, usr, usr.user_team, pad,borrowItem.borrow_date,borrowItem.return_date,idx)<0:
                        result = result and False
                    else:
                        tmp['type']=pad.pad_type
                        tmp['id']=pad.pad_id
                        tmp['team']=pad.user_team
                        tmp['return_date']=borrowItem.borrow_date.strftime('%Y-%m-%d')
                        tmp['borrower']=borrowItem.borrower_name
                        result.append(tmp)
            idx=idx+1
        #返回
        return result

    #设备归还（直接写入数据库）
    #param user:当前登录的用户
    #param device_id:设备id
    #param return_date:归还日期
    #param device_cond：设备状态
    def manager_return(self,user,device_id,return_date,device_cond):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if user.user_role>=3:
            device = self.session_uav.query(Device).filter(Device.device_id==device_id,Device.user_team==user.user_team).first()
            battery= self.session_uav.query(Battery).filter(Battery.battery_id==device_id,Battery.user_team==user.user_team).first()
            part   = self.session_uav.query(Battery).filter(Parts.parts_id==device_id,Parts.user_team==user.user_team).first()
            pad = self.session_uav.query(Battery).filter(Pad.pad_id == device_id,Pad.user_team==user.user_team).first()
            manager = self.session_uav.query(Manager).filter(Manager.device_id==device_id,Manager.manager_status=='借用').first()
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
                return 2052101

            if idx!=0:
                self.session_uav.query(Manager).filter(Manager.device_id == manager.device_id and Manager.manager_status=='借用').update({Manager.manager_status: '归还',Manager.return_date:return_date}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            else:
                return 2052102


            if idx==1:
                if device_cond=='正常':
                    self.session_uav.query(Device).filter(Device.device_id == manager.device_id).update({Device.device_status: '在库'},synchronize_session=False)
                else:
                    self.session_uav.query(Device).filter(Device.device_id == manager.device_id).update(
                        {Device.device_status: '维修'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            if idx==2:
                if device_cond == '正常':
                    self.session_uav.query(Battery).filter(Battery.battery_id == manager.device_id).update({Battery.battery_status: '在库'},synchronize_session=False)
                else:
                    self.session_uav.query(Battery).filter(Battery.battery_id == manager.device_id).update(
                        {Battery.battery_status: '维修'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            if idx==3:
                if device_cond == '正常':
                    self.session_uav.query(Parts).filter(Parts.parts_id == manager.device_id).update({Parts.parts_status: '在库'},synchronize_session=False)
                else:
                    self.session_uav.query(Parts).filter(Parts.parts_id == manager.device_id).update(
                        {Parts.parts_status: '维修'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            if idx==4:
                if device_cond == '正常':
                    self.session_uav.query(Pad).filter(Pad.pad_id == manager.device_id).update({Pad.pad_status: '在库'},synchronize_session=False)
                else:
                    self.session_uav.query(Pad).filter(Pad.pad_id == manager.device_id).update({Pad.pad_status: '维修'},
                                                                                               synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            return 1
        return 2052103

    #设备归还列表（返回列表显示）
    #param usr:登录用户
    #param returnlist:归还设备列表
    def manager_return_list(self,usr,returnList):
        usrDao=UserDAO()
        roles=usrDao.get_role(usr)
        result = []
        idx = 0
        for returnItem in returnList:
            tmp={}
            device_id = returnItem.device_id
            #判断设备类型
            device = self.session_uav.query(Device).filter(Device.device_id == device_id).first()
            battery = self.session_uav.query(Battery).filter(Battery.battery_id == device_id).first()
            part = self.session_uav.query(Parts).filter(Parts.parts_id == device_id).first()
            pad = self.session_uav.query(Pad).filter(Pad.pad_id == device_id).first()
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
            if idx==0:
                continue
            if status!='出库':
                continue

            if idx==1:
                tmp['type']=device.device_type
                tmp['id']=device.device_id
                tmp['team']=device.user_team
                tmp['return_date']=returnItem.return_date.strftime('%Y-%m-%d')
                tmp['borrower']=self.manager_query_latestBorrower(device.device_id).borrower_name
                result.append(tmp)
            if idx==2:
                tmp['type'] = battery.battery_type
                tmp['id'] = battery.battery_id
                tmp['team'] = battery.user_team
                tmp['return_date'] = returnItem.return_date.strftime('%Y-%m-%d')
                tmp['borrower'] = self.manager_query_latestBorrower(battery.battery_id).borrower_name
                result.append(tmp)
            if idx==3:
                tmp['type'] = part.parts_type
                tmp['id'] = part.parts_id
                tmp['team'] = part.user_team
                tmp['return_date'] = returnItem.return_date.strftime('%Y-%m-%d')
                tmp['borrower'] = self.manager_query_latestBorrower(part.parts_id).borrower_name
                result.append(tmp)
            if idx==4:
                tmp['type'] = pad.pad_type
                tmp['id'] = pad.pad_id
                tmp['team'] = pad.user_team
                tmp['return_date'] = returnItem.return_date.strftime('%Y-%m-%d')
                tmp['borrower'] = self.manager_query_latestBorrower(pad.pad_id).borrower_name
                result.append(tmp)
        #返回
        return result

    #设备查询（查询设备情况）
    #param device_id:设备id
    #param returntime:设备归还时间
    #param borrower:借用人
    #param desc:设备描述
    def manager_query_device(self,device_id,retruntime,borrower,desc):
        device = self.session_uav.query(Device).filter(Device.device_id == device_id).first()
        battery = self.session_uav.query(Battery).filter(Battery.battery_id == device_id).first()
        part = self.session_uav.query(Battery).filter(Parts.parts_id == device_id).first()
        pad = self.session_uav.query(Battery).filter(Pad.pad_id == device_id).first()
        self.session_uav.rollback()
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
            deviceitem['desc'] = desc
        elif idx==2:
            battery = class_to_dict(self.session_uav.query(Battery).filter(Battery.battery_id==device_id).all())
            deviceitem['device_type'] = battery[0]['battery_type']
            deviceitem['device_id'] = battery[0]['battery_id']
            deviceitem['user_team'] = battery[0]['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower
            deviceitem['desc'] = desc
        elif idx==3:
            part = class_to_dict(self.session_uav.query(Parts).filter(Parts.parts_id==device_id).all())
            deviceitem['device_type'] = part[0]['parts_type']
            deviceitem['device_id'] = part[0]['parts_id']
            deviceitem['user_team'] = part[0]['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower
            deviceitem['desc'] = desc
        else:
            pad = class_to_dict(self.session_uav.query(Pad).filter(Pad.pad_id==device_id).all())
            deviceitem['device_type'] = pad[0]['pad_type']
            deviceitem['device_id'] = pad[0]['pad_id']
            deviceitem['user_team'] = pad[0]['user_team']
            deviceitem['return_date'] = retruntime
            deviceitem['borrower'] = borrower
            deviceitem['desc'] = desc
        ret.append(deviceitem)
        return ret

    #根据设备id 查询最后借用的借用人信息
    #param device_id:查询设备id
    #返回最后借用记录信息
    def manager_query_latestBorrower(self,device_id):
        tmpdate= self.session_uav.query(func.max(Manager.borrow_date)).filter(Manager.device_id==device_id).first()
        rs=self.session_uav.query(Manager).filter(Manager.device_id==device_id,Manager.borrow_date==tmpdate[0]).first()
        return rs

#故障设备表管理接口，查询故障，添加故障
#author: Wu Wei
#Version 1.0.0.0
#所有错误代码以0206XXXX开始
class FaultDao:
    def __init__(self):
        self.session_uav = Session_UAV()

    def __del__(self):
        self.session_uav.close()

    #分页查询故障列表
    #param user:当前登录用户
    #param device_ver:设备种类
    #param page_index:当前显示的页码
    #param page_size:每一页展示的数据条数
    def query_list(self,user,device_ver,page_index,page_size):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        q = self.session_uav.query(Fault)
        #本部门设备的故障信息
        q=q.filter(Fault.device_department==user.user_department)
        if device_ver:
            q = q.filter(Fault.device_ver == device_ver)
        allFaults = q.limit(page_size).offset((page_index-1)*page_size).all()
        self.session_uav.rollback()
        items=class_to_dict(allFaults)
        rsItems=[]
        mngr=ManagerDAO()
        for item in items:
            itemMngr = mngr.manager_query_latestBorrower(item['device_id'])
            if itemMngr is not None:
                item['lastborrower']=itemMngr.borrower_name
            else:
                item['lastborrower']=''
            rsItems.append(item)
        return  rsItems

    #查询故障页数
    #param user:当前登录用户
    #param device_ver:设备类型
    #param page_size:每一页的条数
    def query_pages(self,user,device_ver,page_size):
        if device_ver is not None:
            rs= self.session_uav.query(Fault).filter(Fault.device_ver==device_ver,Fault.device_department==user.user_department).count() / page_size + 1
            item = {}
            item['pages'] = rs
            return json.dumps(item)
        else:
            if page_size>0:
                rs= self.session_uav.query(Fault).filter(Fault.device_department==user.user_department).count()/page_size+1
                item = {}
                item['pages'] = rs
                return json.dumps(item)
            else:
                return None

    #查询统计信息
    #param user:统计故障情况
    def query_statistics(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '1' in roles and '5' not in roles:
            #故障原因
            sql = 'select fault_reason,count(*) from tb_fault where fault_finished=0 and device_department=\''+user.user_department+'\' group by fault_reason;'
            rs = self.session_uav.execute(sql).fetchall()
            self.session_uav.rollback()

            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        elif '5' in roles:
            sql = 'select fault_reason,count(*) from tb_fault where fault_finished=0 and device_department=\''+user.user_department+'\' group by fault_reason;'
            rs = self.session_uav.execute(sql).fetchall()
            ret = []
            for i in rs:
                item = {}
                item['name']=i[0]
                item['value']=i[1]
                ret.append(item)
            return json.dumps(ret)
        else:
            return None

    #查询统计故障类别
    def query_types(self):
        sql = 'select device_ver from tb_fault where fault_finished=0 group by device_ver;'
        rs = self.session_uav.execute(sql).fetchall()
        ret = []
        for i in rs:
            item = {}
            item['device_ver'] = i[0]
            ret.append(item)
        return json.dumps(ret)

    #更新设备状态，将设备状态更新为维修
    #param device:设备信息
    #param fault:故障信息
    def updateDevice(self,device,fault):
        self.session_uav.add(fault)
        try:
            self.session_uav.commit()
        except:
            self.session_uav.rollback()
        self.session_uav.query(Device).filter(Device.device_id == fault.device_id).update(
            {Device.device_status: '维修'}, synchronize_session=False)
        try:
            self.session_uav.commit()
        except:
            self.session_uav.rollback()
        fault.device_department = device.device_use_dpartment

    #添加故障信息
    def add_fault(self,user,fault):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)

        device = self.session_uav.query(Device).filter(Device.device_id == fault.device_id).first()
        battery = self.session_uav.query(Battery).filter(Battery.battery_id == fault.device_id).first()
        part = self.session_uav.query(Battery).filter(Parts.parts_id == fault.device_id).first()
        pad = self.session_uav.query(Battery).filter(Pad.pad_id == fault.device_id).first()

        idx = 0
        devicestatus='在库';
        if device:
            idx = 1
            devicestatus = device.device_status
        if battery:
            idx = 2
            devicestatus = battery.battery_status
        if part:
            idx = 3
            devicestatus = part.parts_status
        if pad:
            idx = 4
            devicestatus = pad.pad_status
        if idx==0:
            return 2060601
        if devicestatus != '在库':
            return 2060602


        if '2' in roles and '5' not in roles:
            #不是管理员则需要判断飞机和用户的班组
            if device.user_team==user.user_team:
                if idx == 1:
                    self.updateDevice(device,fault)
                if idx ==2:
                    self.updateDevice(battery, fault)
                if idx == 3:
                    self.updateDevice(part, fault)
                if idx == 4:
                    self.updateDevice(pad, fault)

                #添加fault list
                self.session_uav.add(fault)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1

            else :
                return 2060603
        if '5' in roles:
            if idx == 1:
                self.updateDevice(device, fault)
            if idx == 2:
                self.updateDevice(battery, fault)
            if idx == 3:
                self.updateDevice(part, fault)
            if idx == 4:
                self.updateDevice(pad, fault)
            self.session_uav.add(fault)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        return 2060604

    #故障处理完成，完成的状态有两种分别为维修成功和报废（1,2）
    #param user:当前登录用户信息
    #param faultid:故障id
    #param device:设备信息
    #param device_type:设备类型
    #param result:维修结果（0,1）
    def fault_processUser(self,user,faultid,device,device_type,result):
        if device.user_team == user.user_team:
            tmpfault = self.session_uav.query(Fault).filter(Fault.fault_id == faultid).first()
            tmpfault.fault_finished = result
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            if device_type == 1:
                if result==1:
                    self.session_uav.query(Device).filter(Device.device_id == tmpfault.device_id).update(
                        {Device.device_status: '在库'}, synchronize_session=False)
                else :
                    self.session_uav.query(Device).filter(Device.device_id == tmpfault.device_id).update(
                        {Device.device_status: '报废'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            if device_type == 2:
                if result == 1:
                    self.session_uav.query(Battery).filter(Battery.battery_id == tmpfault.device_id).update(
                        {Battery.battery_status: '在库'}, synchronize_session=False)
                else:
                    self.session_uav.query(Battery).filter(Battery.battery_id == tmpfault.device_id).update(
                        {Battery.battery_status: '报废'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            if device_type == 3:
                if result==1:
                    self.session_uav.query(Parts).filter(Parts.parts_id == tmpfault.device_id).update(
                        {Parts.parts_status: '在库'}, synchronize_session=False)
                else:
                    self.session_uav.query(Parts).filter(Parts.parts_id == tmpfault.device_id).update(
                        {Parts.parts_status: '报废'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
            if device_type == 4:
                if result ==1:
                    self.session_uav.query(Pad).filter(Pad.pad_id == tmpfault.device_id).update({Pad.pad_status: '在库'},
                                                                                             synchronize_session=False)
                else:
                    self.session_uav.query(Pad).filter(Pad.pad_id == tmpfault.device_id).update({Pad.pad_status: '报废'},
                                                                                                synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
        else:
            return 2060701
    def faule_processManager(self,user,faultid,device,device_type,result):
        if device.device_use_dpartment == user.user_department:
            tmpfault = self.session_uav.query(Fault).filter(Fault.fault_id == faultid).first()
            tmpfault.fault_finished = result
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            if device_type == 1:
                if result==1:
                    self.session_uav.query(Device).filter(Device.device_id == tmpfault.device_id).update(
                        {Device.device_status: '在库'}, synchronize_session=False)
                else :
                    self.session_uav.query(Device).filter(Device.device_id == tmpfault.device_id).update(
                        {Device.device_status: '报废'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
            if device_type == 2:
                if result == 1:
                    self.session_uav.query(Battery).filter(Battery.battery_id == tmpfault.device_id).update(
                        {Battery.battery_status: '在库'}, synchronize_session=False)
                else:
                    self.session_uav.query(Battery).filter(Battery.battery_id == tmpfault.device_id).update(
                        {Battery.battery_status: '报废'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
            if device_type == 3:
                if result==1:
                    self.session_uav.query(Parts).filter(Parts.parts_id == tmpfault.device_id).update(
                        {Parts.parts_status: '在库'}, synchronize_session=False)
                else:
                    self.session_uav.query(Parts).filter(Parts.parts_id == tmpfault.device_id).update(
                        {Parts.parts_status: '报废'}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
            if device_type == 4:
                if result ==1:
                    self.session_uav.query(Pad).filter(Pad.pad_id == tmpfault.device_id).update({Pad.pad_status: '在库'},
                                                                                             synchronize_session=False)
                else:
                    self.session_uav.query(Pad).filter(Pad.pad_id == tmpfault.device_id).update({Pad.pad_status: '报废'},
                                                                                                synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
        else:
            return 2060801
    
    #故障处理完成
    #param user:登录用户信息
    #param fault:错误id
    def finished_fault(self,user,fault_id):
        usrDao = UserDAO()
        roles = usrDao.get_role(user)
        fault=self.session_uav.query(Fault).filter(Fault.fault_id==fault_id).first()
        self.session_uav.rollback()

        device = self.session_uav.query(Device).filter(Device.device_id == fault.device_id).first()
        battery = self.session_uav.query(Battery).filter(Battery.battery_id == fault.device_id).first()
        part = self.session_uav.query(Battery).filter(Parts.parts_id == fault.device_id).first()
        pad = self.session_uav.query(Battery).filter(Pad.pad_id == fault.device_id).first()

        idx = 0
        if device:
            idx = 1
        if battery:
            idx = 2
        if part:
            idx = 3
        if pad:
            idx = 4
        if idx == 0:
            return 2060901

        #普通用户只能处理本班组的设备
        if '2' in roles and '5' not in roles:
            if idx==1:
                self.faule_processManager(user,fault_id,device,idx,1)
            if idx==2:
                self.faule_processManager(user, fault_id, battery,idx,1)
            if idx==3:
                self.faule_processManager(user, fault_id, part,idx,1)
            if idx==4:
                self.faule_processManager(user, fault_id, pad,idx,1)
        #管理员可以处理本所的设备
        if '5' in roles:
            if idx==1:
                self.faule_processManager(user,fault_id,device,idx,1)
            if idx==2:
                self.faule_processManager(user, fault_id, battery,idx,1)
            if idx==3:
                self.faule_processManager(user, fault_id, part,idx,1)
            if idx==4:
                self.faule_processManager(user, fault_id, pad,idx,1)
        return 1

    #设备报废
    #param user:用户信息
    #param fault_id:错误id
    def scrap_fault(self,user,fault_id):
        usrDao = UserDAO()
        roles = usrDao.get_role(user)
        fault=self.session_uav.query(Fault).filter(Fault.fault_id==fault_id).first()
        self.session_uav.rollback()

        device = self.session_uav.query(Device).filter(Device.device_id == fault.device_id).first()
        battery = self.session_uav.query(Battery).filter(Battery.battery_id == fault.device_id).first()
        part = self.session_uav.query(Battery).filter(Parts.parts_id == fault.device_id).first()
        pad = self.session_uav.query(Battery).filter(Pad.pad_id == fault.device_id).first()

        idx = 0
        if device:
            idx = 1
        if battery:
            idx = 2
        if part:
            idx = 3
        if pad:
            idx = 4
        if idx == 0:
            return 2061001

        #普通用户只能处理本班组的设备
        if '2' in roles and '5' not in roles:
            if idx==1:
                return self.faule_processManager(user,fault_id,device,idx,2)
            if idx==2:
                return self.faule_processManager(user, fault_id, battery,idx,2)
            if idx==3:
                return self.faule_processManager(user, fault_id, part,idx,2)
            if idx==4:
                return self.faule_processManager(user, fault_id, pad,idx,2)
        #管理员可以处理本所的设备
        if '5' in roles:
            if idx==1:
                return  self.faule_processManager(user,fault_id,device,idx,2)
            if idx==2:
                return self.faule_processManager(user, fault_id, battery,idx,2)
            if idx==3:
                return self.faule_processManager(user, fault_id, part,idx,2)
            if idx==4:
                return self.faule_processManager(user, fault_id, pad,idx,2)

        return -1


#设备故障报告
#故障报告的查询更新操作
#author：Wu Wei
#version: 1.0.0.0
#所有错误代码以0207XXXX开始
class FaultReportDao:
    def __init__(self):
        self.session_uav = Session_UAV()

    def __del__(self):
        self.session_uav.close()

    #根据id查询故障报告
    #param fpid:故障id
    def query(self,fpid):
        rs = self.session_uav.query(FaultReport).filter(FaultReport.fault_report_id==fpid).all()
        return class_to_dict(rs)

    #更新故障报告
    #param user:用户信息
    #param faultreport:故障报告
    def update(self,user,faultreport):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '3' in roles:
            rs = self.session_uav.query(FaultReport).filter(FaultReport.fault_report_id == faultreport.fault_report_id).first()
            if(rs!=None):
                if(faultreport.fault_report_device_id!=None):
                    rs.fault_report_device_id = faultreport.fault_report_device_id
                if (faultreport.fault_report_line_name != None):
                    rs.fault_report_line_name = faultreport.fault_report_line_name
                if (faultreport.fault_report_towerRange != None):
                    rs.fault_report_towerRange = faultreport.fault_report_towerRange
                if (faultreport.fault_report_date != None):
                    rs.fault_report_date = faultreport.fault_report_date
                if (faultreport.fault_report_flyer != None):
                    rs.fault_report_flyer = faultreport.fault_report_flyer
                if (faultreport.fault_report_wether != None):
                    rs.fault_report_wether = faultreport.fault_report_wether
                if (faultreport.fault_report_observer != None):
                    rs.fault_report_observer = faultreport.fault_report_observer
                if (faultreport.fault_time != None):
                    rs.fault_time = faultreport.fault_time
                if (faultreport.fault_crash_position != None):
                    rs.fault_crash_position = faultreport.fault_crash_position
                if (faultreport.fault_crash_desc != None):
                    rs.fault_crash_desc = faultreport.fault_crash_desc
                if (faultreport.fault_crash_operation != None):
                    rs.fault_crash_operation = faultreport.fault_crash_operation
                if (faultreport.fault_crash_damage != None):
                    rs.fault_crash_damage = faultreport.fault_crash_damage
                if (faultreport.fault_crash_electric != None):
                    rs.fault_crash_electric = faultreport.fault_crash_electric
                if (faultreport.fault_crash_around != None):
                    rs.fault_crash_around = faultreport.fault_crash_around
            else:
                tmp = FaultReport()
                tmp.fault_report_id=faultreport.fault_report_id
                tmp.fault_report_device_id = faultreport.fault_report_device_id
                tmp.fault_report_line_name = faultreport.fault_report_line_name
                tmp.fault_report_towerRange = faultreport.fault_report_towerRange
                tmp.fault_report_date = faultreport.fault_report_date
                tmp.fault_report_flyer = faultreport.fault_report_flyer
                tmp.fault_report_wether = faultreport.fault_report_wether
                tmp.fault_report_observer = faultreport.fault_report_observer
                tmp.fault_time = faultreport.fault_time
                tmp.fault_crash_position = faultreport.fault_crash_position
                tmp.fault_crash_desc = faultreport.fault_crash_desc
                tmp.fault_crash_operation = faultreport.fault_crash_operation
                tmp.fault_crash_damage = faultreport.fault_crash_damage
                tmp.fault_crash_electric = faultreport.fault_crash_electric
                tmp.fault_crash_around = faultreport.fault_crash_around
                self.session_uav.add(tmp)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2070201

#借调申请管理
#author：Wu Wei
#version: 1.0.0.0
#所有错误代码以0208XXXX开始
class ApprovalDao:
    def __init__(self):
        self.session_uav = Session_UAV()
        self.session_usr = Session_User()
    def __del__(self):
        self.session_uav.close()
        self.session_usr.close()

    #故障查询
    #param user:当前登录用户
    def approval_query(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '4' in roles and  '5' not in roles:
            rs=self.session_uav.query(Approval).filter(Approval.approval_team==user.user_team,Approval.approval_status==0).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs=self.session_uav.query(Approval).filter(Approval.approval_status==0).all()
            return class_to_dict(rs)
        else:
            return None

    #根据申请人查询故障
    #param user:当前登录用户
    def approval_query_apply(self,user):
        rs=self.session_uav.query(Approval).filter(Approval.apply_person==user.user_id).all()
        return class_to_dict(rs)

    #根据故障审批人查询故障（如果为超级用户则可以查看所有审批，部门管理员能看到提交给自己的审批）
    #param user:审批人
    def approval_query_approve(self,user):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)
        if '4' in roles and  '5' not in roles:
            rs=self.session_uav.query(Approval).filter(Approval.approval_person==user.user_id).all()
            return class_to_dict(rs)
        elif '5' in roles:
            rs=self.session_uav.query(Approval).filter(Approval.approval_status==0).all()
            return class_to_dict(rs)
        else:
            return 2080301       

    #批准借调
    #param user:当前登录用户
    #param approval:审批记录
    def approval_aggree(self,user,approval):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)

        if '4' in roles and '5' not in roles:
            if user.user_team != approval.approval_team:
                self.session_uav.query(Approval).filter(Approval.apply_person == approval.apply_person).update(
                    {Approval.approval_status: 1}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
        elif '5' in roles:
            self.session_uav.query(Approval).filter(Approval.apply_person == approval.apply_person).update(
                {Approval.approval_status: 1}, synchronize_session=False)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2080401
    
    #不批准借调
    #param user:当前登录用户
    #param approval:审批记录
    def approval_disagree(self,user,approval):
        usrDao=UserDAO()
        roles=usrDao.get_role(user)

        if '4' in roles and '5' not in roles:
            if user.user_team == approval.approval_team:
                self.session_uav.query(Approval).filter(Approval.apply_person == approval.apply_person).update(
                    {Approval.approval_status: 2}, synchronize_session=False)
                try:
                    self.session_uav.commit()
                except:
                    self.session_uav.rollback()
                return 1
        elif '5' in roles:
            self.session_uav.query(Approval).filter(Approval.apply_person == approval.apply_person).update(
                {Approval.approval_status: 2}, synchronize_session=False)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
                return 1
        return 2080501
    
    #添加借调申请
    #param user:当前登录用户
    #param approval:提交申请
    def approval_add(self,user,approval):
        usrDao=UserDAO()

        #提交的批准人无权限批准
        userApproval=self.session_usr.query(User).filter(User.user_id==approval.approval_person).first()
        if userApproval is None:
            return 2080601
        roleApproval = usrDao.get_role(userApproval)
        if '4' not in roleApproval and '5' not in roleApproval:
            return 2080602

        roles=usrDao.get_role(userApproval)
        if '4' in roles or '5' in roles:
            if user.user_team!=approval.approval_team:
                return 2080603

            approvalTmp = self.session_uav.query(Approval).filter(Approval.apply_person==approval.apply_person).first()
            #提交申请后申请未审核则状态为0，审核通过则状态为1，审核未空过则状态为2
            #在提交新的申请时首先判断原有申请是否处理，如果未处理则先处理原有申请
            if(approvalTmp !=None and approvalTmp.approval_status!=0):
                self.approval_finished(approval.apply_person)
            
            self.session_uav.merge(approval)
            try:
                self.session_uav.commit()
            except:
                self.session_uav.rollback()
            return 1
        else:
            return 2080604

    #将申请添加到申请处理备份库中
    def approval_finished(self,apply_person):
        #构造申请备份库
        approval_cur = self.session_uav.query(Approval).filter(Approval.apply_person==apply_person).first()
        self.session_uav.rollback()
        approval_db=Approval_db()
        approval_db.apply_person=approval_cur.apply_person
        approval_db.approval_person=approval_cur.approval_person
        approval_db.approval_team=approval_cur.approval_team
        approval_db.return_date=approval_cur.return_date
        approval_db.device_ver=approval_cur.device_ver
        approval_db.device_number=approval_cur.device_number
        approval_db.battery_ver = approval_cur.battery_ver
        approval_db.battery_number=approval_cur.battery_number
        approval_db.pad_ver = approval_cur.pad_ver
        approval_db.pad_number=approval_cur.pad_number
        approval_db.approval_status=approval_cur.approval_status
        approval_db.approval_reason = approval_cur.approval_reason
        approval_db.approval_desc = approval_cur.approval_desc
        try:
            self.session_uav.add(approval_db)
            self.session_uav.commit()
        except:
            self.session_uav.rollback()
        self.session_uav.delete(approval_cur)
        try:
            self.session_uav.commit()
        except:
            self.session_uav.rollback()

#巡检计划管理
#author：Wu Wei
#version: 1.0.0.0
#所有错误代码以0209XXXX开始
class PlanDao:
    def __init__(self):
        self.session_uav = Session_UAV()
        self.session_usr = Session_User()
    def __del__(self):
        self.session_uav.close()
        self.session_usr.close()

    #查询巡检计划
    #param linename: 线路名称
    #param team :巡检班组
    #param datast:起始日期
    #param dataend:终止日期
    def searchPlan(self,linename,team,datest,dateend):
        q=self.session_uav.query(Plan)
        if linename != None:
            q=q.filter(Plan.plan_line==linename)
        if team != None:
            q=q.filter(Plan.plan_team==team)
        if datest!=None:
            q.q.filter(Plan.plan_time>datest)
        if dateend!=None:
            q.q.filter(Plan.plan_time<dateend)
        rs = q.all()
        return class_to_dict(rs)