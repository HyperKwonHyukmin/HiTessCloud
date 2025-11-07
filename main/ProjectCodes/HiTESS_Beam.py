import os
import subprocess
from main import *
import os
import subprocess
from datetime import datetime

def AnalysisMongo(analysisType, user_id, user_name, user_company, user_dept):
    current_utc_time = round(datetime.utcnow().timestamp() * 1000)
    analysisData = {
        'userID': user_id,
        'userName': user_name,
        'userCompany': user_company,
        'userDept': user_dept,
        'analysisType': analysisType,
        'analysisTime': current_utc_time,
        'status': "None",
    }
    mongo.db.members.find_one_and_update({'userID': user_id}, {"$inc": {"analysisCNT": 1}})
    result = mongo.db.analysis.insert_one(analysisData)


def TrussAssessmentRun(programDirectory, receiveFile, userFolder, user_id, user_name, user_company, user_dept):
  try:
    programEXE = os.path.join(programDirectory, "TrussAssessment.exe")
    runText = f"{programEXE} {receiveFile}"

    AnalysisMongo('Truss 구조 해석', user_id, user_name, user_company, user_dept, userFolder, runText, [".xlsx", ".f06", ".op2"])

  except Exception as e:
      print("TrussAssessment 예외 발생:", e)


def LadderRun(user_id, user_name, user_company, user_dept):
    AnalysisMongo("Ladder 구조해석", user_id, user_name, user_company, user_dept)


def ModuleGroupUnitRun(programeName, user_id, user_name, user_company, user_dept):
    if programeName == "ModuleUnit":
        mongorProgramName = programeName + "_HiTESS"
    else:
        mongorProgramName = programeName + "_HiTESS"
    AnalysisMongo(mongorProgramName, user_id, user_name, user_company, user_dept)


def CsvToBdfRun(user_id, user_name, user_company, user_dept):
    AnalysisMongo("CsvToBdf", user_id, user_name, user_company, user_dept)