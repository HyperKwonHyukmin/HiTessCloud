from flask import Flask
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
# from bson.objectid import ObjectId
from flask import abort
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from datetime import timedelta, timezone
from datetime import datetime
import time
import math
import os
import threading
import os
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import csv

# 플라스크 객체 app 생성
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/HHI_member"

# flash를 사용하려면 secret_key를 추가해야함, flash 사용을 위한 필수
app.secret_key = 'super secret key'

# 세션 유지시간 설정 : 8시간
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

# PyMong 객체 생성
mongo = PyMongo(app)

# 플라스크 내에서 사용할 모듈 import
# from .common import login_required, format_datetime
# from . import index
# from . import blueprint_calc
# from . import blueprint_nas
# from . import blueprint_truss
# from . import blueprint_beam
# from . import blueprint_member
# from . import blueprint_pipe
# from . import blueprint_hitessbeam

#
# # Blueprint 사용을 위한 등록
# app.register_blueprint(blueprint_calc.blueprint)
# app.register_blueprint(blueprint_nas.blueprint)
# app.register_blueprint(blueprint_truss.blueprint)
# app.register_blueprint(blueprint_beam.blueprint)
# app.register_blueprint(blueprint_member.blueprint)
# app.register_blueprint(blueprint_pipe.blueprint)
# app.register_blueprint(blueprint_hitessbeam.blueprint)


userID = "A507238"
userName = "김병훈"
company = "HD 현대중공업"
userDept = "구조시스템연구실"
userPos = "책임매니저"
current_utc_time = round(datetime.now(timezone.utc).timestamp() * 1000)

# 회원 가입 정보를 DB에 저장
userData = {
    'userID': userID,  # 사번
    'userName': userName,  # 회원이름
    'userCompany': company,  # 회사이름
    'userDept': userDept,  # 회원부서
    'userPos': userPos,  # 회원직급
    'joinTime': current_utc_time,  # 회원가입 시간
    'joinCNT': 0,  # 회원로그인 횟수
    'analysisCNT': 0,  # 회원 프로그램 사용 횟수
    'isMember': 'False',  # 관리자 승인 유무
    'permissions': {}
}
members = mongo.db.members
members.insert_one(userData)


