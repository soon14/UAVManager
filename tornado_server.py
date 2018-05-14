#coding=utf-8
#!/usr/bin/python

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from Server import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(8091)  #flask默认的端口
IOLoop.instance().start()