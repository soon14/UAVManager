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
from UAVManagerEntity import User, Lines, Towers,Photo, class_to_dict
from UAVManagerDAO import UserDAO

from flask import Flask, request ,jsonify
from flask import Response,make_response

cf = ConfigParser.ConfigParser()
cf.read("config.conf")
power_host = cf.get("power_account", "db_host")
power_port = cf.getint("power_account", "db_port")
power_user = cf.get("power_account", "db_user")
power_pass = cf.get("power_account", "db_pass")
power_name = cf.get("power_account","db_name")

secret_key = cf.get('token','SECRET_KEY')

engine_pwoer = create_engine('mysql+mysqldb://' + power_user + ':' + power_pass + '@' + power_host + ':' + str(power_port) + '/' + power_name+'?charset=utf8')
Session_Power= sessionmaker(bind=engine_pwoer)
session_power = Session_Power()

class LinesDao:
    def query_lines(self):
        rs = session_power.query(Lines).all()
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
    def query_towers(self):
        rs = session_power.query(Towers).all()
        return class_to_dict(rs)

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

class PhotoDao:
    def query_photos(self):
        rs = session_power.query(Photo).all()
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
        photo = Photo(photo_voltage=voltage,photo_line=line_id,photo_tower_id=tower_id,photo_path=path,photo_classify=classify)
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