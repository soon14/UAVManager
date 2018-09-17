#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:图片后台分类工具，图片上传后根据图片的坐标将图片自动分类到杆塔目录下
compiler:python2.7.x

created by  : Frank.Wu
company     : GEDI
created time: 2018.09.14
version     : version 1.0.0.0
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from PIL import Image
from PIL.ExifTags import TAGS

from PowerLineDao import LinesDao, TowerDao,PhotoDao

# 获取线路下所有杆塔位置信息
# param linename:线路名称
# 返回杆塔信息
def GetTowerPosition(linename):
    towerPosDao = TowerDao()
    towers=towerPosDao.query_towers(linename);
    return towers

# 获取照片中的经纬度信息
# param photoPath : 照片路径
# 返回坐标信息
def GetPhotoCoordinate(photoPath):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(photoPath)
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        print 'IOERROR ' + photoPath
    return ret
