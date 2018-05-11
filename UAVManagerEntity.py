#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer,String,DateTime

#use orm
EntityBase = declarative_base()
def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
EntityBase.to_dict=to_dict

class User(EntityBase):
    #table name
    __tablename__ = 'user'
    user_id = Column(String(20),primary_key=True)
    user_password = Column(String(32))
    user_name= Column(String(45))
    user_phone=Column(String(11))
    user_team =Column(String(45))
    user_role =Column(Integer)

class Role(EntityBase):
    __tablename__ = 'role'
    role_id = Column(Integer,primary_key=True)
    role_name = Column(String(45))
    role_basic = Column(String(14))

class Role_basic(EntityBase):
    __tablename__ = 'role_basic'
    role_basic_id = Column(Integer,primary_key=True)
    role_basic_type = Column(String(45))

class Manager(EntityBase):
    __tablename__ = 'tb_manager'
    manager_id = Column(Integer,primary_key=True)
    device_id = Column(Integer)
    device_ver= Column(String(50))
    device_type = Column(String(50))
    user_team = Column(String(50))
    borrower_name = Column(String(45))
    borrow_date = Column(DateTime)
    approver_name = Column(String(45))
    manager_status = Column(String(10))
    return_date = Column(DateTime)
    return_desc = Column(String(1024))

class Device(EntityBase):
    __tablename__ = 'tb_device'
    device_id = Column(Integer, primary_key=True)
    device_ver = Column(String(45))
    device_type = Column(String(45))
    uad_code = Column(String(45))
    device_fact = Column(String(45))
    device_date = Column(String(45))
    user_team = Column(String(45))
    uad_camera= Column(String(45))
    uav_yuntai=Column(String(45))
    uad_rcontrol=Column(String(45))
    device_status=Column(String(10))
    device_use_number=Column(Integer)

class Battery(EntityBase):
    __tablename__ = 'tb_battery'
    battery_id = Column(Integer, primary_key=True)
    battery_ver = Column(String(45))
    battery_type=Column(String(45))
    battery_fact=Column(String(45))
    battery_date=Column(String(45))
    user_team=Column(String(45))
    battery_status=Column(String(10))
    battery_use_number=Column(Integer)

class Pad(EntityBase):
    __tablename__ = 'tb_pad'
    pad_id = Column(Integer,primary_key=True)
    pad_ver=Column(String(45))
    pad_type=Column(String(45))
    pad_fact=Column(String(45))
    pad_date=Column(String(45))
    user_team = Column(String(45))
    pad_status=Column(String(45))
    pad_use_number=Column(Integer)

class Parts(EntityBase):
    __tablename__ = 'tb_parts'
    parts_id = Column(Integer,primary_key=True)
    parts_ver=Column(String(45))
    parts_type=Column(String(45))
    parts_fact=Column(String(45))
    parts_date=Column(String(45))
    user_team = Column(String(45))
    parts_status=Column(String(45))
    parts_use_number=Column(Integer)

class Approval(EntityBase):
    __tablename__ = 'tb_approval'
    apply_person=Column(String(45),primary_key=True)
    approval_team=Column(String(45))
    device_ver=Column(String(45))
    device_number=Column(Integer)
    battery_ver = Column(String(45))
    battery_number=Column(Integer)
    pad_ver = Column(String(45))
    pad_number=Column(Integer)
    approval_status=Column(Integer)

class Fault(EntityBase):
    __tablename__ = 'tb_fault'
    fault_id = Column(Integer, primary_key=True)
    device_id = Column(Integer)
    device_ver=Column(String(45))
    fault_date = Column(String(45))
    fault_reason=Column(String(45))
    fault_deal = Column(String(45))
    fault_finished = Column(Integer)

class FaultReport(EntityBase):
    __tablename__ = 'tb_fault_report'
    fault_report_id = Column(Integer,primary_key=True)
    fault_report_device_id = Column(Integer)
    fault_report_line_name = Column(String(45))
    fault_report_towerRange=Column(String(45))
    fault_report_date = Column(String(45))
    fault_report_flyer=Column(String(45))
    fault_report_wether=Column(String(45))
    fault_report_observer=Column(String(45))
    fault_time=Column(String(45))
    fault_crash_position=Column(String(256))
    fault_crash_desc=Column(String(1024))
    fault_crash_operation=Column(String(1024))
    fault_crash_damage=Column(String(1024))
    fault_crash_electrric=Column(String(1024))
    fault_crash_around=Column(String(1024))

def class_to_dict(obj):
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__
    if is_list or is_set:
        obj_arr = []
        for o in obj:
            #trans obj to dict
            dict = {}
            dict.update(o.to_dict())
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        dict.update(obj.__dict__)
        return dict