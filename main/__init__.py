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
from datetime import timedelta
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
from .common import login_required, format_datetime
from . import index
# from . import blueprint_calc
# from . import blueprint_nas
from . import blueprint_truss
from . import blueprint_beam
from . import blueprint_member
from . import blueprint_pipe
from . import blueprint_hitessbeam

#
# # Blueprint 사용을 위한 등록
# app.register_blueprint(blueprint_calc.blueprint)
# app.register_blueprint(blueprint_nas.blueprint)
app.register_blueprint(blueprint_truss.blueprint)
app.register_blueprint(blueprint_beam.blueprint)
app.register_blueprint(blueprint_member.blueprint)
app.register_blueprint(blueprint_pipe.blueprint)
app.register_blueprint(blueprint_hitessbeam.blueprint)


def start_user_statistics_background_task(interval_sec=3600):
    # MongoDB 연결
    client = MongoClient("mongodb://localhost:27017/")
    db = client["HHI_member"]
    analysis_collection = db["analysis"]
    members_collection = db["members"]

    # 프로그램별 절감 해석공수 정의 (임의로 설정)
    labor_savings = {
        "Truss 해석 모델 구축": 30.0,
        "Truss 구조 해석": 30.0,
        "Mooring Fitting 구조 안정성 평가": 30.0,
        "HitessBeam": 6.0,
        "Unknown": 0.0
    }

    def job(interval_sec=3600):
        while True:
            try:
                # 사용자 정보 캐싱
                member_info_dict = {}
                for member in members_collection.find({}, {
                    "_id": 0,
                    "userID": 1,
                    "userName": 1,
                    "userDept": 1,
                    "userCompany": 1,
                    "userPos": 1
                }):
                    member_info_dict[member["userID"]] = {
                        "userName": member.get("userName", ""),
                        "userDept": member.get("userDept", ""),
                        "userCompany": member.get("userCompany", ""),
                        "userPos": member.get("userPos", "")
                    }

                # 로그 리스트 수집
                rows = []
                for record in analysis_collection.find({}, {
                    "_id": 0, "userID": 1, "analysisType": 1, "analysisTime": 1
                }):
                    user_id = record.get("userID")
                    analysis_type = record.get("analysisType")
                    timestamp = record.get("analysisTime")

                    # 시간 포맷 변환
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')

                    # 사용자 정보
                    info = member_info_dict.get(user_id, {
                        "userName": "Unknown",
                        "userDept": "Unknown",
                        "userCompany": "Unknown",
                        "userPos": "Unknown"
                    })

                    # 절감 해석공수 추가
                    savings = labor_savings.get(analysis_type, labor_savings["Unknown"])

                    rows.append([
                        info["userName"],
                        info["userCompany"],
                        user_id,
                        info["userDept"],
                        analysis_type,
                        formatted_time,
                        savings
                    ])

                # 기존 CSV 읽기
                addCsv = r"C:\Users\HHI\KMH\Log_data\MUnit_Use.csv"
                existing_rows = []
                try:
                    df = pd.read_csv(addCsv, encoding="utf-8-sig")
                    # 첫 번째 열(인덱스) 제외하고 데이터 추출
                    if df.columns[0].lower() in ['index', 'unnamed: 0']:
                        df = df.iloc[:, 1:]  # 첫 번째 열 스킵
                    # 열 이름을 현재 코드와 일치시키기
                    df.columns = ["이름", "회사", "사번", "부서", "사용프로그램", "접속시간", "절감 해석공수"]
                    existing_rows = df.values.tolist()
                except FileNotFoundError:
                    print(f"[정보] 기존 CSV 파일이 없습니다: {addCsv}")
                except Exception as e:
                    print(f"[오류] 기존 CSV 읽기 실패: {e}")

                # 기존 데이터와 새 데이터 합치기
                combined_rows = existing_rows + rows

                # 시간 순 정렬
                combined_rows.sort(key=lambda x: x[-2])  # 접속시간 기준 정렬

                saveCsv = r"C:\Users\HHI\KHM\Palantir\HiTESS_UserStastics\HiTESS_log.csv"
                # CSV 저장
                with open(saveCsv, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(["이름", "회사", "사번", "부서", "사용프로그램", "접속시간", "절감 해석공수"])
                    writer.writerows(combined_rows)

                print(f"[완료] 사용자 로그가 CSV로 저장되었습니다: {saveCsv}")

            except Exception as e:
                print(f"[오류] {e}")

            import time
            time.sleep(interval_sec)

    threading.Thread(target=job, daemon=True).start()

start_user_statistics_background_task(interval_sec=10800)
# def start_user_statistics_background_task(interval_sec=3600):
#     # MongoDB 연결
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["HHI_member"]
#     analysis_collection = db["analysis"]
#     members_collection = db["members"]
#
#     # 프로그램별 절감 해석공수 정의 (임의로 설정)
#     labor_savings = {
#         "Truss 해석 모델 구축": 30.0,
#         "Truss 구조 해석": 30.0,
#         "Mooring Fitting 구조 안정성 평가": 30.0,
#         "HitessBeam": 6.0,
#         "Unknown": 0.0
#     }
#
#     def job(interval_sec=3600):
#         while True:
#             try:
#                 # 사용자 정보 캐싱
#                 member_info_dict = {}
#                 for member in members_collection.find({}, {
#                     "_id": 0,
#                     "userID": 1,
#                     "userName": 1,
#                     "userDept": 1,
#                     "userCompany": 1,
#                     "userPos": 1
#                 }):
#                     member_info_dict[member["userID"]] = {
#                         "userName": member.get("userName", ""),
#                         "userDept": member.get("userDept", ""),
#                         "userCompany": member.get("userCompany", ""),
#                         "userPos": member.get("userPos", "")
#                     }
#
#                 # 로그 리스트 수집
#                 rows = []
#                 for record in analysis_collection.find({}, {
#                     "_id": 0, "userID": 1, "analysisType": 1, "analysisTime": 1
#                 }):
#                     user_id = record.get("userID")
#                     analysis_type = record.get("analysisType")
#                     timestamp = record.get("analysisTime")
#
#                     # 시간 포맷 변환
#                     dt = datetime.fromtimestamp(timestamp / 1000)
#                     formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
#
#                     # 사용자 정보
#                     info = member_info_dict.get(user_id, {
#                         "userName": "Unknown",
#                         "userDept": "Unknown",
#                         "userCompany": "Unknown",
#                         "userPos": "Unknown"
#                     })
#
#                     # 절감 해석공수 추가
#                     savings = labor_savings.get(analysis_type, labor_savings["Unknown"])
#
#                     rows.append([
#                         info["userName"],
#                         info["userCompany"],
#                         user_id,
#                         info["userDept"],
#                         analysis_type,
#                         formatted_time,
#                         savings  # 절감 해석공수 추가
#                     ])
#
#                 # 시간 순 정렬
#                 rows.sort(key=lambda x: x[-2])  # 접속시간 기준 정렬 (새 열 추가로 인덱스 조정)
#
#                 # 저장 경로
#                 output_path = os.path.join(r"C:\Users\HHI\KHM\Palantir\HiTESS_UserStastics", "HiTESS_log.csv")
#
#                 # CSV 저장
#                 with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
#                     writer = csv.writer(f)
#                     writer.writerow(["이름", "회사", "사번", "부서", "사용프로그램", "접속시간", "절감 해석공수"])
#                     writer.writerows(rows)
#
#                 print(f"[완료] 사용자 로그가 CSV로 저장되었습니다: {output_path}")
#
#             except Exception as e:
#                 print(f"[오류] {e}")
#
#             import time
#             time.sleep(interval_sec)
#
#     threading.Thread(target=job, daemon=True).start()
#
#
# start_user_statistics_background_task(interval_sec=10800)
