#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer,String,DateTime,FLOAT,Date
import json
from datetime import date



#use orm
EntityBase = declarative_base()
def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}
EntityBase.to_dict=to_dict


def convert(obj):
    if(isinstance(obj,date)):
        return obj.strftime('%Y-%m-%d')
    else:
        return obj

#########################################################################用户管理
class User(EntityBase):
    #table name
    __tablename__ = 'user'
    user_id = Column(String(20),primary_key=True)
    user_password = Column(String(32))
    user_name= Column(String(45))
    user_phone=Column(String(11))
    user_number=Column(String(45))
    user_department=Column(String(45))
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

#############################################################################无人机管理
class Manager(EntityBase):
    __tablename__ = 'tb_manager'
    manager_id = Column(Integer,primary_key=True)
    device_id = Column(Integer)
    device_ver= Column(String(50))
    device_type = Column(String(50))
    user_team = Column(String(50))
    borrower_name = Column(String(45))
    borrow_date = Column(Date)
    approver_name = Column(String(45))
    manager_status = Column(String(10))
    return_date = Column(Date)
    return_desc = Column(String(1024))

class Device(EntityBase):
    __tablename__ = 'tb_device'
    device_id = Column(Integer, primary_key=True)
    device_ver = Column(String(45))
    device_type = Column(String(45))
    uad_code = Column(String(45))
    device_fact = Column(String(45))
    device_date = Column(Date)
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
    battery_date=Column(Date)
    user_team=Column(String(45))
    battery_status=Column(String(10))
    battery_use_number=Column(Integer)

class Pad(EntityBase):
    __tablename__ = 'tb_pad'
    pad_id = Column(Integer,primary_key=True)
    pad_ver=Column(String(45))
    pad_type=Column(String(45))
    pad_fact=Column(String(45))
    pad_date=Column(Date)
    user_team = Column(String(45))
    pad_status=Column(String(45))
    pad_use_number=Column(Integer)

class Parts(EntityBase):
    __tablename__ = 'tb_parts'
    parts_id = Column(Integer,primary_key=True)
    parts_ver=Column(String(45))
    parts_type=Column(String(45))
    parts_fact=Column(String(45))
    parts_date=Column(Date)
    user_team = Column(String(45))
    parts_status=Column(String(45))
    parts_use_number=Column(Integer)

class Approval(EntityBase):
    __tablename__ = 'tb_approval'
    apply_person=Column(String(45),primary_key=True)
    approval_person = Column(String(45))
    approval_team=Column(String(45))
    device_ver=Column(String(45))
    device_number=Column(Integer)
    battery_ver = Column(String(45))
    battery_number=Column(Integer)
    pad_ver = Column(String(45))
    pad_number=Column(Integer)
    approval_status=Column(Integer)

class Approval_db(EntityBase):
    __tablename__ = 'tb_approval_db'
    approval_id=Column(Integer,primary_key=True)
    apply_person=Column(String(45))
    approval_person = Column(String(45))
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
    fault_date = Column(Date)
    fault_reason=Column(String(45))
    fault_deal = Column(String(45))
    fault_finished = Column(Integer)

class FaultReport(EntityBase):
    __tablename__ = 'tb_fault_report'
    fault_report_id = Column(Integer,primary_key=True)
    fault_report_device_id = Column(Integer)
    fault_report_line_name = Column(String(45))
    fault_report_towerRange=Column(String(45))
    fault_report_date = Column(Date)
    fault_report_flyer=Column(String(45))
    fault_report_wether=Column(String(45))
    fault_report_observer=Column(String(45))
    fault_time=Column(String(45))
    fault_crash_position=Column(String(256))
    fault_crash_desc=Column(String(1024))
    fault_crash_operation=Column(String(1024))
    fault_crash_damage=Column(String(1024))
    fault_crash_electric=Column(String(1024))
    fault_crash_around=Column(String(1024))

##############################################################################线路杆塔管理
class Lines(EntityBase):
    __tablename__='tb_lines'
    lines_id = Column(Integer,primary_key=True)
    lines_name=Column(String(45))
    lines_construct_date = Column(Date)
    lines_voltage = Column(String(45))
    lines_work_team = Column(String(45))
    lines_incharge = Column(String(45))
    deleted = Column(Integer)

class Towers(EntityBase):
    __tablename__='tb_tower'
    tower_id = Column(Integer,primary_key=True)
    tower_linename = Column(String(128))
    tower_idx = Column(Integer)
    tower_type = Column(String(45))
    tower_date = Column(Date)
    tower_span_small = Column(FLOAT)
    tower_span_horizonal = Column(FLOAT)
    tower_span_vertical = Column(FLOAT)
    tower_rotation_direction = Column(String(45))
    tower_rotation_degree = Column(FLOAT)
    tower_height = Column(FLOAT)
    tower_lat = Column(FLOAT)
    tower_lng = Column(FLOAT)
    tower_elevation = Column(FLOAT)
    tower_descriptor = Column(String(256))
    deleted = Column(Integer)

class LightArrest(EntityBase):
    __tablename__='tb_tower'
    light_arrest_id = Column(Integer)
    light_arrest_type = Column(String(45))
    light_arrest_factor = Column(String(128))
    light_arrest_counter_type = Column(String(128))
    light_arrest_install_date = Column(Date)
    light_arrest_gap = Column(String(45))
    light_arrest_descriptor = Column(String(128))

class Insulator(EntityBase):
    __tablename__ = 'tb_tower'
    insulator_id = Column(Integer)
    insulator_type = Column(String(45))
    insulator_number_strand = Column(Integer)
    insulator_strands = Column(Integer)
    insulator_install_date = Column(Date)
    insulator_factor = Column(String(128))
    insulator_creepagedistance = Column(FLOAT)
    insulator_distanceStd = Column(String(45))
    insulator_std_required = Column(String(45))
    insulator_double = Column(String(45))
    insulator_double_hang = Column(String(45))
    insulator_descriptor = Column(String(128))

class OPGW(EntityBase):
    __tablename__ = 'tb_tower'
    opgw_id = Column(Integer)
    opgw_region=Column(String(45))
    opgw_type = Column(String(45))
    opgw_date = Column(Date)
    opgw_factor = Column(String(128))
    opgw_descriptor = Column(String(128))

class Photo(EntityBase):
    __tablename__="tb_photo"
    photo_id = Column(Integer,primary_key=True)
    photo_line = Column(Integer)
    photo_tower_id = Column(Integer)
    photo_path=Column(String(256))
    photo_classify=Column(String(45))
    photo_date = Column(Date)

class TowerPart(EntityBase):
    __tablename__="tb_part_dict"
    tb_partid = Column(Integer,primary_key=True)
    tb_partname = Column(Integer)

class DefectLevel(EntityBase):
    __tablename__="tb_defect_level"
    tb_defect_level_id = Column(Integer,primary_key=True)
    tb_defect_level = Column(String(45))

class DefectPart(EntityBase):
    __tablename__="tb_defect_part"
    tb_defect_part_id = Column(Integer,primary_key=True)
    tb_defect_part_name = Column(String(45))

class Defect(EntityBase):
    __tablename__="tb_defect"
    tb_defect_id = Column(Integer,primary_key=True)
    tb_defect_towerid = Column(Integer)
    tb_defect_lineid = Column(Integer)
    tb_defect_photoid=Column(Integer)
    tb_defect_level=Column(Integer)
    tb_defect_part = Column(String(45))
    tb_defect_desc = Column(String(256))



def class_to_dict(obj):
    is_list = obj.__class__ == [].__class__
    is_set = obj.__class__ == set().__class__
    if is_list or is_set:
        obj_arr = []
        for o in obj:
            #trans obj to dict
            dict = {}
            tmpdict=o.to_dict()
            for key in tmpdict:
                dict[key]=convert(tmpdict[key])

            #tmp=json.dumps(tmpdict,default=ComplexEncoder)
           # jtmp=json.loads(tmp)
            #dict.update(json.loads(tmp))
            obj_arr.append(dict)
        return obj_arr
    else:
        dict = {}
        tmpdict = obj.to_dict()
        for key in tmpdict:
            dict[key] = convert(tmpdict[key])
        return dict