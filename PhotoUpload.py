#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

import ConfigParser
import json
from flask_restful import Resource
from flask import Flask, request ,jsonify
from flask import Response,make_response
from werkzeug import secure_filename
from PowerLineDao import PhotoDao
from UAVManagerDAO import UserDAO
from UAVManagerEntity import Photo
from datetime import datetime

import datetime
ALLOWED_EXTENSIONS = set(['png', 'jpg','JPG', 'jpeg', 'gif'])
cf = ConfigParser.ConfigParser()
cf.read("config.conf")
save_folder = cf.get("picture","UPLOAD_FOLDER")
save__picture_folder = cf.get("picture","IMAGE_UPLOAD_FOLDER")
database_folder = cf.get("picture","DATABASEFOLDER")
nowTime=datetime.datetime.now().strftime('%Y%m%d')

class FileUpload(Resource):
    def __init__(self):
        self.photoDao = PhotoDao()
        self.userDao = UserDAO()

    def allowed_file(self,filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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

            file_folder = save_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+data['date']+'/'+classify
            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)
            if image and self.allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(file_folder, filename))
                db_folder=database_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+classify
                rs = self.photoDao.add_photo(voltage,line_id,tower_id,classify,os.path.join(db_folder, filename),date)
                if rs == 1:
                    return make_response(jsonify({'seccess': 'upload success'}), 200)
            else:
                return make_response(jsonify({'error': 'param error'}), 401)
        else:
            return make_response(jsonify({'error': 'param error'}), 401)

    def get(self):
        return self.post()

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