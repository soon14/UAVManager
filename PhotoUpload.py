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

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
cf = ConfigParser.ConfigParser()
cf.read("config.conf")
save_folder = cf.get("picture","UPLOAD_FOLDER")
database_folder = cf.get("picture","DATABASEFOLDER")

class FileUpload(Resource):
    def __init__(self):
        self.photoDao = PhotoDao
        self.userDao = UserDAO

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def post(self):
        if (request.data != ""):
            data = json.loads(request.data)
            #token = data['token'] #要不要登录
            line_id = data['lineId']
            tower_id = data['towerId']
            voltage  = data['voltage']
            classify = data['classify']
            image = request.files['image']
            file_folder = save_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+classify
            if not os.path.isdir(file_folder):
                os.makedirs(file_folder)
            if image and self.allowed_file(image.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(file_folder, filename))

            db_folder=database_folder+'/'+voltage+'/'+line_id+'/'+tower_id+'/'+classify
            return self.photoDao.add_photo(voltage,line_id,tower_id,classify,os.path.join(db_folder, filename))
        else:
            return make_response(jsonify({'error': 'param error'}), 401)

