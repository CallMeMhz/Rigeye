#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
import operator
from flask import Flask

import conn

# 配置Flask
app = Flask('rigeye')
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='so fuckin secret',
    USERNAME='root',
    PASSWORD='toor',
    DATABASE_URL='localhost',
    DATABASE_PORT=27017
))
app.config.from_object('config')
app.config.from_envvar('RIGEYE_SETTINGS', silent=True)

from views import *

# 连接数据库
client = conn.connect_mongodb(app)
db = client['rigeye']


if __name__ == '__main__':
	import scheduler
	scheduler.load_jobs()
	app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)

