#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
desc:对于视频上传的请求响应,前端采用web uploader进行分块上传，后端分块接收并写入文件中，最后通过将分块数据写入文件
compiler:python2.7.x

created by  : Frank.Wu
company     : GEDI
created time: 2018.08.16
version     : version 1.0.0.0
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import json
import ConfigParser

from flask_restful import Resource
from flask_restful import reqparse
from flask import Flask, request ,jsonify
from flask import Response,make_response
from PowerLineDao import VideoDataDAO
from UAVManagerDAO import UserDAO
from UAVManagerEntity import Video
from datetime import datetime

parser = reqparse.RequestParser()
parser.add_argument('linename', type=str, location='args')

cf = ConfigParser.ConfigParser()
cf.read("config.conf")
video_folder = cf.get("picture","DATABASEFOLDER")
video_url    = cf.get("picture","DATABASETHUMBNAIL")

#根据线路查询线路视频
class VideoSearchRoute(Resource):
    def __init__(self):
        self.dao = VideoDataDAO()
        self.userDao = UserDAO()

    def post(self):
        args = parser.parse_args()
        linename = args.get('linename')
        sttime   = datetime.strptime(args.get('date'), '%Y-%m-%d').date()
        rs=self.dao.query_video(linename,sttime);
        return rs
    def get(self):
        return self.post()

#上传部分视频
class VideoUploadPartRoute(Resource):
    def __init__(self):
        self.dao = VideoDataDAO()
        self.userDao = UserDAO()

    def post(self):
        task = request.form.get('task_id')  # 获取文件的唯一标识符
        chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
        filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

        upload_file = request.files['file']
        upload_file.save('%s/%s' %video_folder, filename)  # 保存分片到本地
        return make_response(jsonify({'success': filename+'上传成功'}), 200)
    def get(self):
        return self.post()

#上传完成之后将数据合并
class VideoUploadMergeRoute(Resource):
    def __init__(self):
        self.dao = VideoDataDAO()
        self.userDao = UserDAO()

    def post(self):
        target_filename = request.args.get('filename')  # 获取上传文件的文件名
        task = request.args.get('task_id')  # 获取文件的唯一标识符
        chunk = 0  # 分片序号
        with open('%s/%s' %video_folder, target_filename, 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = './upload/%s%d' % (task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                except IOError, msg:
                    break

                chunk += 1
                os.remove(filename)  # 删除该分片，节约空间

        #将文件写入数据库中
        return make_response(jsonify({'success': target_filename + '上传成功'}), 200)

    def get(self):
        return self.post()