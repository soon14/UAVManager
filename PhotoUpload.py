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
import UAVPhotoClassify
from UAVManagerEntity import Photo
from datetime import datetime
from PIL import Image
import datetime

ALLOWED_EXTENSIONS = set(['png', 'jpg','JPG', 'jpeg', 'gif'])
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
class PhotoClassifyUpload(Resource):
    # 检查文件后缀是否符合要求（是否是照片数据）
    # param filename:照片文件的文件名
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    # 生成缩略图
    # param pathSrc:输入图片文件路径
    # param pathThumbnail:输入缩略图路径
    def generateThumbnail(self, pathSrc, pathThumbnail):
        im = Image.open(pathSrc)
        factor = 0.2
        w, h = im.size
        im.thumbnail((w * factor, h * factor))
        im.save(pathThumbnail, 'jpeg')

    def post(self):
        if (request.form != ""):
            data = request.form
            # token = data['token'] #要不要登录
            #line_id = data['lineid']
            #classify = data['classify']

            line_name=data['linename']
            voltage = data['voltage']
            date=datetime.datetime.strptime(data['date'],'%Y-%m-%d').date()
            image = request.files['image']

            # 获取文件存储路径
            file_folder = save_folder
            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)
            if image and self.allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(file_folder, filename))
            classify=UAVPhotoClassify()
            towers = classify.GetTowerPosition(line_name)
            #进行分类并获取缩略图
            classifyRs = classify.ClassifyPhoto(towers,os.path.join(file_folder, filename),date,save_folder)
            basePath = classifyRs[0]
            self.generateThumbnail(os.path.join(file_folder, filename),os.path.join(thumbnail_folder, filename))
            #添加到数据库中
            towerIdx = classifyRs[1]
            lineid = classifyRs[2]
            rs = self.photoDao.add_photo(voltage, lineid, towers[towerIdx].t, classify, os.path.join(database_folder, basePath),
                                         os.path.join(thumbnail_database_folder, basePath), date)
            return make_response(jsonify({'seccess': '照片上传成功'}), 200)

    def get(self):
        return self.post()
