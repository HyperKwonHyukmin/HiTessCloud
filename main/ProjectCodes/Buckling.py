import os
import subprocess
from main import *
import os
import subprocess
from datetime import datetime

def AnalysisMongoOnlyCalc(analysisType, user_id, user_name, user_company, user_dept):
    current_utc_time = round(datetime.utcnow().timestamp() * 1000)
    analysisData = {
        'userID': user_id,
        'userName': user_name,
        'userCompany': user_company,
        'userDept': user_dept,
        'analysisType': analysisType,
        'analysisTime': current_utc_time,
        'status': "Running",
        'files': []
    }

    mongo.db.members.find_one_and_update({'userID': user_id}, {"$inc": {"analysisCNT": 1}})
    result = mongo.db.analysis.insert_one(analysisData)

    status = "Complete"

    mongo.db.analysis.update_one(
        {'_id': result.inserted_id},
        {
            '$set': {
                'status': status,
                'files': None
            }
        })

def ColumnBucklingAssessmentRun(programDirectory, user_id, user_name, user_company, user_dept):
  try:

    AnalysisMongoOnlyCalc('기둥 좌굴 사용 하중 계산 프로그램', user_id, user_name, user_company, user_dept)

  except Exception as e:
      print("기둥 좌굴 사용 하중 계산 프로그램 예외 발생:", e)