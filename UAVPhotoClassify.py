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
import shutil
import sys
import os
reload(sys)
import math

sys.setdefaultencoding('utf8')

from PIL import Image
from PIL.ExifTags import TAGS


from PowerLineDao import LinesDao, TowerDao,PhotoDao

class UAVPhotoClassify:
    # 获取线路下所有杆塔位置信息
    # param linename:线路名称
    # 返回杆塔信息
    def GetTowerPosition(self,linename):
        towerPosDao = TowerDao()
        towers=towerPosDao.query_towers(linename);
        return towers

    # 获取照片中的经纬度信息
    # param photoPath : 照片路径
    # 返回坐标信息
    def GetPhotoCoordinate(self,photoPath):
        """Get embedded EXIF data from image file."""
        ret = {}
        try:
            img = Image.open(photoPath)
            if hasattr( img, '_getexif' ):
                exifinfo = img._getexif()
                if exifinfo!= None:
                    if 34853 in exifinfo:
                        gpsInfo = exifinfo[34853]
                        latTuple = gpsInfo[2]
                        lngTuple = gpsInfo[4]
                        lat = float(latTuple[0][0]) / float(latTuple[0][1]) + float(latTuple[1][0]) / float(
                            latTuple[1][1]) / 60.0 + float(latTuple[2][0]) / \
                              float(latTuple[2][1]) / 3600.0
                        lng = float(lngTuple[0][0]) / float(lngTuple[0][1]) + float(lngTuple[1][0]) / float(
                            lngTuple[1][1]) / 60.0 + float(lngTuple[2][0]) / \
                              float(lngTuple[2][1]) / 3600.0
                        ret['lat'] = lat
                        ret['lng'] = lng
                    else:
                        ret['lat'] = 0.0
                        ret['lng'] = 0.0
                else:
                    ret['lat']=0.0
                    ret['lng']=0.0
            else:
                ret['lat'] = 0.0
                ret['lng'] = 0.0
        except IOError:
            print 'IOERROR ' + photoPath
        return ret

    # 移动文件到指定目录下（通过剪切方式）
    # param srcfile : 源文件路径
    # param dstfile : 目标文件路径
    def MoveFile(self,srcfile,dstfile):
        if not os.path.isfile(srcfile):
            print "%s not exist!"%(srcfile)
        else:
            fpath,fname=os.path.split(dstfile)    #分离文件名和路径
            if not os.path.exists(fpath):
                os.makedirs(fpath)                #创建路径
            shutil.move(srcfile,dstfile)          #移动文件
            #print "move %s -> %s"%( srcfile,dstfile)


    # 获取照片中的经纬度信息
    # param towers  : 线路所有杆塔信息
    # param photoPath : 照片路径
    # param date : 拍照日期
    # param basefolder : 根文件夹目录
    # 返回坐标信息
    def ClassifyPhoto(self,towers,photoPath,date,basefolder):
        #纬度一度的差异 直接计算差异比坐标转换之后再计算虽然在精度上下降了，但是效率上得到了很大的提高
        # 综合考虑之后采用直接通过经度和纬度差异的方式进行计算
        unitLat = 111000.0
        photoCoordinate = self.GetPhotoCoordinate(photoPath)
        dis = []
        for towerItem in towers:
            unitLng = unitLat*math.cos(math.radians(photoCoordinate['lat']))
            dLat = (towerItem['tower_lat']-photoCoordinate['lat'])*unitLat*(towerItem['tower_lat']-photoCoordinate['lat'])*unitLat
            dLng = (towerItem['tower_lng']-photoCoordinate['lng'])*unitLng*(towerItem['tower_lng']-photoCoordinate['lng'])*unitLng
            dis.append(math.sqrt(dLat+dLng))
        index = dis.index(min(dis))

        #将文件移动到对应的文件夹下
        daoLine=LinesDao()
        line=daoLine.query_line_fuzzy(towers[index]['tower_linename'])
        filename=os.path.basename(photoPath)

        #构建目标路径
        basePath = '\\'+str(line[0]['lines_voltage'])+'\\'+str(line[0]['lines_id'])+'\\'+str(towers[index]['tower_id'])+'\\'+date+'\\未分类\\'+filename
        distPath= basefolder+basePath

        #移动文件夹
        self.MoveFile(photoPath,distPath)
        return (basePath,index,line[0]['lines_id'])

