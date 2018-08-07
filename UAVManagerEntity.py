#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, FLOAT, Date, ForeignKey
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
    user_id = Column(String(20),primary_key=True)       #用户id 用户唯一标识
    user_password = Column(String(32))                  #用户密码
    user_name= Column(String(45))                       #用户名
    user_phone=Column(String(11))                       #用户电话号码
    user_number=Column(String(45))                      #用户编号
    user_department=Column(String(45))                  #所属部门
    user_team =Column(String(45))                       #所属班组
    user_role =Column(Integer)                          #用户权限

class Role(EntityBase):
    __tablename__ = 'role'
    role_id = Column(Integer,primary_key=True)          #权限
    role_name = Column(String(45))                      #权限名称
    role_basic = Column(String(14))                     #所包含的基础权限

class Role_basic(EntityBase):
    __tablename__ = 'role_basic'
    role_basic_id = Column(Integer,primary_key=True)
    role_basic_type = Column(String(45))

#############################################################################无人机管理
class Manager(EntityBase):
    __tablename__ = 'tb_manager'
    manager_id = Column(Integer,primary_key=True)       #管理id
    device_id = Column(Integer)                         #设备id
    device_ver= Column(String(50))                      #设备类型
    device_type = Column(String(50))                    #设备种类
    device_department = Column(String(45))              #设备所属部门
    user_team = Column(String(50))                      #所属班组
    borrower_name = Column(String(45))                  #借用人
    borrow_date = Column(Date)                          #借用日期
    approver_name = Column(String(45))                  #审批人
    manager_status = Column(String(10))                 #借用状态
    return_date = Column(Date)                          #归还日期
    return_desc = Column(String(1024))                  #描述

class Device(EntityBase):
    __tablename__ = 'tb_device'
    device_id = Column(Integer, primary_key=True)       #设备ID（设备的唯一标识，考虑修改为字符类型）
    device_ver = Column(String(45))                     #设备版本信息
    device_type = Column(String(45))                    #设备类型
    uad_code = Column(String(45))                       #设备机身编码
    device_fact = Column(String(45))                    #维护人
    device_date = Column(Date)                          #设备日期
    user_team = Column(String(45))                      #使用班组
    uad_camera= Column(String(45))                      #相机型号（不使用了）
    uav_yuntai=Column(String(45))                       #云台相机
    uad_rcontrol=Column(String(45))                     #民航局编码
    device_status=Column(String(10))                    #设备状态：在库 出库 维修 报废 丢失
    device_use_number=Column(Integer)                   #设备使用次数
    device_use_dpartment = Column(String(45))           #设备使用部门

class Battery(EntityBase):
    __tablename__ = 'tb_battery'
    battery_id = Column(Integer, primary_key=True)      #电池id
    battery_ver = Column(String(45))                    #电池版本信息
    battery_type=Column(String(45))                     #电池类型
    battery_fact=Column(String(45))                     #维护人
    battery_date=Column(Date)                           #电池日期
    user_team=Column(String(45))                        #使用班组
    battery_status=Column(String(10))                   #电池状态：在库 出库 维修 报废 丢失
    battery_use_number=Column(Integer)                  #电池使用次数
    battery_use_dpartment=Column(String(45))            #电池使用部门

class Pad(EntityBase):
    __tablename__ = 'tb_pad'
    pad_id = Column(Integer,primary_key=True)
    pad_ver=Column(String(45))
    pad_type=Column(String(45))
    pad_fact=Column(String(45))
    pad_date=Column(Date)
    user_team = Column(String(45))
    pad_status=Column(String(45))#在库 出库 维修 报废 丢失
    pad_use_number=Column(Integer)
    pad_use_dpartment=Column(String(45))

class Parts(EntityBase):
    __tablename__ = 'tb_parts'
    parts_id = Column(Integer,primary_key=True)
    parts_ver=Column(String(45))
    parts_type=Column(String(45))
    parts_fact=Column(String(45))
    parts_date=Column(Date)
    user_team = Column(String(45))
    parts_status=Column(String(45))#在库 出库 维修 报废 丢失
    parts_use_number=Column(Integer)
    parts_use_dpartment=Column(String(45))

class Approval(EntityBase):
    __tablename__ = 'tb_approval'
    apply_person=Column(String(45),primary_key=True)
    approval_person = Column(String(45))
    approval_team=Column(String(45))
    device_ver=Column(String(45))
    return_date = Column(Date)
    device_number=Column(Integer)
    battery_ver = Column(String(45))
    battery_number=Column(Integer)
    pad_ver = Column(String(45))
    pad_number=Column(Integer)
    approval_reason = Column(String(256))
    approval_desc = Column(String(256))
    approval_status=Column(Integer)

class Approval_db(EntityBase):
    __tablename__ = 'tb_approval_db'
    approval_id=Column(Integer,primary_key=True)
    apply_person = Column(String(45))
    approval_person = Column(String(45))
    approval_team=Column(String(45))
    return_date = Column(Date)
    device_ver=Column(String(45))
    device_number=Column(Integer)
    battery_ver = Column(String(45))
    battery_number=Column(Integer)
    pad_ver = Column(String(45))
    pad_number=Column(Integer)
    approval_reason = Column(String(256))
    approval_desc = Column(String(256))
    approval_status=Column(Integer)

class Fault(EntityBase):
    __tablename__ = 'tb_fault'
    fault_id = Column(Integer, primary_key=True)        #故障id
    device_id = Column(Integer)                         #设备id
    device_ver=Column(String(45))                       #设备型号
    device_department = Column(String(45))              #所属部门
    fault_date = Column(Date)                           #故障日期
    fault_reason=Column(String(45))                     #故障原因
    fault_deal = Column(String(45))                     #故障处理方式
    fault_finished = Column(Integer)                    #0维修 1维修完成 2报废

class FaultReport(EntityBase):
    __tablename__ = 'tb_fault_report'
    fault_report_id = Column(Integer,primary_key=True)  #报告id
    fault_report_device_id = Column(Integer)            #设备id
    fault_report_line_name = Column(String(45))         #线路名称
    fault_report_towerRange=Column(String(45))          #杆塔范围
    fault_report_date = Column(Date)                    #报告日期
    fault_report_flyer=Column(String(45))               #飞手
    fault_report_wether=Column(String(45))              #天气
    fault_report_observer=Column(String(45))            #观察人员
    fault_time=Column(String(45))                       #故障时间
    fault_crash_position=Column(String(256))            #故障位置
    fault_crash_desc=Column(String(1024))               #故障描述
    fault_crash_operation=Column(String(1024))          #引起故障的操作
    fault_crash_damage=Column(String(1024))             #故障造成的损失
    fault_crash_electric=Column(String(1024))           #故障造成的电力设备损毁
    fault_crash_around=Column(String(1024))

##############################################################################线路杆塔管理
class Lines(EntityBase):
    __tablename__='tb_lines'
    lines_id = Column(Integer,primary_key=True)         #线路ID
    lines_name=Column(String(45))                       #线路名称
    lines_construct_date = Column(Date)                 #建造日期
    lines_voltage = Column(String(45))                  #电压等级
    lines_work_team = Column(String(45))                #维护班组
    lines_incharge = Column(String(45))                 #线路负责人
    deleted = Column(Integer)                           #是否被删除

class Towers(EntityBase):
    __tablename__='tb_tower'
    tower_id = Column(Integer,primary_key=True)
    tower_linename = Column(String(128))             #所在线路名称
    tower_idx = Column(Integer)                      #杆塔序号
    tower_type = Column(String(45))                  #杆塔类型
    tower_date = Column(Date)                        #杆塔日期
    tower_span_small = Column(FLOAT)                 #小号侧杆塔距离
    tower_span_horizonal = Column(FLOAT)             #水平距离
    tower_span_vertical = Column(FLOAT)              #垂直距离
    tower_rotation_direction = Column(String(45))    #转角方向
    tower_rotation_degree = Column(FLOAT)            #转角角度
    tower_height = Column(FLOAT)                     #杆塔高度
    tower_lat = Column(FLOAT)                        #纬度
    tower_lng = Column(FLOAT)                        #经度
    tower_elevation = Column(FLOAT)                  #高程
    tower_descriptor = Column(String(256))           #杆塔描述
    tower_lightarrest_type = Column(String(45))      #避雷器类型
    tower_lightarrest_factory = Column(String(45))   #避雷器厂家
    tower_lightarrest_number_type=Column(String(45)) #避雷器计数器型号
    tower_lightarrest_date = Column(Date)            #避雷器安装日期
    tower_lightarrest_gap = Column(String(45))       #避雷器是否有间隙
    tower_lightarrest_desc = Column(String(256))     #避雷器描述
    tower_insulator_strandtype = Column(String(45))  #绝缘子串类
    tower_insulator_material = Column(String(45))    #绝缘子材质
    tower_insulator_type = Column(String(45))        #绝缘子型号
    tower_insulator_strandnumber = Column(Integer)   #绝缘子单串只数
    tower_insulator_strand = Column(Integer)         #绝缘子串数
    tower_insulator_date = Column(Date)              #安装日期
    tower_insulator_factory = Column(String(45))     #绝缘子厂家
    tower_insulator_creepagedistance = Column(FLOAT) #爬电比距
    tower_insulator_distanceStd = Column(String(45)) #比距标准
    tower_insulator_required = Column(String(45))    #是否符合标准
    tower_insulator_double = Column(String(45))      #悬垂串是否为双串
    tower_insulator_doublehang = Column(String(45))  #悬垂串是否为双串挂点
    tower_insulator_desc = Column(String(256))       #绝缘子描述
    tower_opgw_span = Column(String(45))             #杆塔段
    tower_opgw_type = Column(String(45))             #导线型号
    tower_opgw_date = Column(Date)                   #投运日期
    tower_opgw_factory = Column(String(45))          #生产厂家
    tower_opgw_desc = Column(String(256))            #备注
    deleted = Column(Integer)

class LightArrest(EntityBase):
    __tablename__='tb_lightarrest'
    light_arrest_id = Column(Integer,primary_key=True)
    light_arrest_type = Column(String(45))
    light_arrest_factor = Column(String(128))
    light_arrest_counter_type = Column(String(128))
    light_arrest_install_date = Column(Date)
    light_arrest_gap = Column(String(45))
    light_arrest_descriptor = Column(String(128))

class Insulator(EntityBase):
    __tablename__ = 'tb_insulator'
    insulator_id = Column(Integer,primary_key=True)
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
    __tablename__ = 'tb_opgw'
    opgw_id = Column(Integer,primary_key=True)
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
    photo_thumbnail_path=Column(String(256))
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

class DataService(EntityBase):
    __tablename__ = "tb_dataservice"
    tb_dataservice_id=Column(Integer,primary_key=True)
    tb_dataservice_linename=Column(String(256))
    tb_dataservice_url = Column(String(256))
    tb_dataservice_type = Column(Integer)
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