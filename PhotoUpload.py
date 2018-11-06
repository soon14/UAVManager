#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
desc:此文件实现照片上传功能，将照片文件上传到文件存储中并将记录写入数据库
     另外此文件还支持绘制后的纯照片数据的上传以及信息写回，采用的SQL中间件为为SQLAlchemy；
compiler:python2.7.x

created by  : Frank.Wu
company     : GEDI
created time: 2018.08.16
version     : version 1.0.0.0
"""


import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

import ConfigParser
import json,base64
from flask_restful import Resource
from flask import Flask, request ,jsonify
from flask import Response,make_response
from werkzeug import secure_filename
from PowerLineDao import PhotoDao
from UAVManagerDAO import UserDAO
from UAVPhotoClassify import UAVPhotoClassify
from UAVManagerEntity import Photo
from datetime import datetime
from PIL import Image
import datetime
import threading

ALLOWED_EXTENSIONS = set(['png', 'jpg','JPG', 'jpeg', 'gif','bmp','BMP'])
cf = ConfigParser.ConfigParser()
cf.read("config.conf")
save_folder = cf.get("picture","UPLOAD_FOLDER")
thumbnail_folder=cf.get("picture","UPLOAD_THUMBNAIL")
save__picture_folder = cf.get("picture","IMAGE_UPLOAD_FOLDER")
database_folder = cf.get("picture","DATABASEFOLDER")
thumbnail_database_folder = cf.get("picture","DATABASETHUMBNAIL")
nowTime=datetime.datetime.now().strftime('%Y%m%d')

#普通照片上传功能
class FileUpload(Resource):
    def __init__(self):
        self.photoDao = PhotoDao()
        self.userDao = UserDAO()

    #检查文件后缀是否符合要求（是否是照片数据）
    #param filename:照片文件的文件名
    def allowed_file(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    #生成缩略图
    #param pathSrc:输入图片文件路径
    #param pathThumbnail:输入缩略图路径
    def generateThumbnail(self,pathSrc,pathThumbnail):
        im = Image.open(pathSrc)
        factor=0.2
        w, h = im.size
        im.thumbnail((w *factor, h*factor))
        im.save(pathThumbnail,'jpeg')

    def post(self):
        if (request.form != ""):
            data = request.form
            #token = data['token'] #要不要登录
            line_id = data['lineid']
            tower_id = data['towerid']
            voltage = data['voltage']
            classify = data['classify']
            date=datetime.datetime.strptime(data['date'],'%Y-%m-%d').date()
            image = request.files['image']

            #获取文件存储路径
            file_folder = save_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
            thumbnail =thumbnail_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)
            if not os.path.isdir(thumbnail):
                os.makedirs(thumbnail)
            if image and self.allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(file_folder, filename))
                self.generateThumbnail(os.path.join(file_folder, filename),os.path.join(thumbnail, filename))
                #文件服务器浏览路径
                db_folder=database_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
                db_thumbnail=thumbnail_database_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
                rs = self.photoDao.add_photo(voltage,line_id,tower_id,classify,os.path.join(db_folder, filename),os.path.join(db_thumbnail, filename),date)
                if rs == 1:
                    return make_response(jsonify({'seccess': '照片上传成功'}), 200)
            else:
                return make_response(jsonify({'error': '照片参数输入错误','errorcode':10000000}), 401)
        else:
            return make_response(jsonify({'error': '照片参数输入错误','errorcode':10000000}), 401)

    def get(self):
        return self.post()

#绘制照片并上传
class FileUploadDraw(Resource):
    def __init__(self):
        self.photoDao = PhotoDao()
        self.userDao = UserDAO()

    def allowed_file(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def generateThumbnail(self,pathSrc,pathThumbnail):
        im = Image.open(pathSrc)
        factor=0.2
        w, h = im.size
        im.thumbnail((w *factor, h*factor))
        im.save(pathThumbnail)

    def post(self):
        if (request.form != ""):
            data = json.loads(request.data)
            #token = data['token'] #要不要登录
            photo_id = data['photoid']
            line_id = str(data['lineid'])
            tower_id = str(data['towerid'])
            voltage = data['voltage']
            classify = data['classify']
            date=datetime.datetime.strptime(data['date'],'%Y-%m-%d').date()
            filename=data['name']
            image = base64.b64decode(data['image'])
            file_folder = save_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
            thumbnail =thumbnail_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify

            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)
            if not os.path.isdir(thumbnail):
                os.makedirs(thumbnail)
            if image and self.allowed_file(filename):
                fileImage = open(os.path.join(file_folder, filename), 'wb')
                fileImage.write(image)
                fileImage.close()
                #image.save(os.path.join(file_folder, filename))
                self.generateThumbnail(os.path.join(file_folder, filename),os.path.join(thumbnail, filename))
                db_folder=database_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
                db_thumbnail=thumbnail_database_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
                #rs = self.photoDao.add_photo(voltage,line_id,tower_id,classify,os.path.join(db_folder, filename),os.path.join(db_thumbnail, filename),date)
                #if rs == 1:
                return make_response(jsonify({'success': '照片上传成功'}), 200)
            else:
                return make_response(jsonify({'error': '照片参数输入错误', 'errorcode': 10000000}), 401)
        else:
            return make_response(jsonify({'error': '照片参数输入错误', 'errorcode': 10000000}), 401)

    def get(self):
        return self.post()

#上传图片
class ImageUpload(Resource):
    def allowed_file(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def post(self):
        if (request.form != ""):
            image = request.files['image']

            file_folder = save__picture_folder+'/'+nowTime
            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)
            if image and self.allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(file_folder, filename))
                return make_response(jsonify({'seccess': 'image upload success'}), 200)
        else:
            return make_response(jsonify({'error': 'param error'}), 401)

#上传图片并分类

# 生成缩略图
# param pathSrc:输入图片文件路径
# param pathThumbnail:输入缩略图路径
def generateThumbnail(pathSrc, pathThumbnail):
    im = Image.open(pathSrc)
    factor = 0.2
    w, h = im.size
    im.thumbnail((w * factor, h * factor))
    ext=os.path.splitext(pathThumbnail)[1]
    if(ext=='.png' or ext=='.PNG'):
        im.save(pathThumbnail, 'png')
    if (ext == '.jpg' or ext == '.JPG'):
        im.save(pathThumbnail, 'jpeg')
    if(ext=='.gif' or ext=='.GIF'):
        im.save(pathThumbnail, 'gif')
    if (ext == '.tif' or ext == '.TIF'):
        im.save(pathThumbnail, 'tif')
    if (ext == '.bmp' or ext == '.BMP'):
        im.save(pathThumbnail, 'bmp')

#图片分类处理线程
# param linename:线路名称
# param voltage: 电压等级
# param date:照片拍摄时间
# param fileNames:文件名数组
# param imagePaths:照片路径数组
def photoClassifyThread(linename,voltage,date,fileNames,imagePaths):
    classify = UAVPhotoClassify()
    towers = classify.GetTowerPosition(linename)
    photoDao = PhotoDao()

    classifyTowerRs=[]
    # 进行分类并获取缩略图
    for i in range(len(fileNames)):
        classifyRs = classify.ClassifyPhoto(towers, imagePaths[i], date, save_folder)
        if classifyRs==None:
            return None

        basePath = classifyRs[0]
        paththunmnail=thumbnail_folder+basePath
        dirthumbnail=os.path.dirname(paththunmnail)
        if not os.path.isdir(dirthumbnail):
            os.makedirs(dirthumbnail)
        generateThumbnail(os.path.join(save_folder+basePath),paththunmnail)
        # 添加到数据库中
        towerIdx = classifyRs[1]
        lineid = classifyRs[2]
        rs = photoDao.add_photo(voltage, lineid, towers[towerIdx]['tower_id'], '未分类', database_folder+basePath,
                                  thumbnail_database_folder+ basePath, datetime.datetime.strptime(date,'%Y-%m-%d').date())

        idxTower = int(int(towers[towerIdx]['tower_idx'])*100)
        idxLevel1 = int(idxTower//100)
        idxLevel2 = int((idxTower%100)//10)
        idxLevel3 = int((idxTower%10))
        strIdxTower = str(idxLevel1)
        if(idxLevel2 != 0):
            strIdxTower+='+'+str(idxLevel2)
        if (idxLevel3 != 0):
            strIdxTower += '+' + str(idxLevel3)
        classifyTowerRs.append(strIdxTower)
    return classifyTowerRs

class PhotoClassifyUpload(Resource):
    # 检查文件后缀是否符合要求（是否是照片数据）
    # param filename:照片文件的文件名
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def post(self):
        if (request.form != ""):
            data = request.form
            # token = data['token'] #要不要登录
            #line_id = data['lineid']
            #classify = data['classify']

            line_name=data['linename']
            voltage = data['voltage']
            date=datetime.datetime.strptime(data['date'],'%Y-%m-%d').date()
            image = request.files
            file_folder = save_folder
            # 获取文件存储路径
            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)

            fileNames=[]
            imagePaths=[]
            for key, file in image.iteritems():
                #print file.filename
                if file and self.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    fileNames.append(filename)
                    file.save(os.path.join(file_folder, filename))
                    imagePaths.append(os.path.join(file_folder, filename))
                else:
                    return make_response(jsonify({'error': '文件为空或文件格式不支持'}), 400)

            #如果不做多线程可能会卡死
            rs=photoClassifyThread(line_name,voltage,data['date'],fileNames,imagePaths)
            if rs==None:
                return make_response(jsonify({'error': '图片不含GPS信息无法上传'}), 400)
            #进行分类
            #t = threading.Thread(target=photoClassifyThread, args=(line_name,voltage,date,fileNames,imagePaths))
            #t.start()
            return make_response(jsonify({'seccess': '照片上传成功','classify':rs[0]}),200)

    def get(self):
        return self.post()