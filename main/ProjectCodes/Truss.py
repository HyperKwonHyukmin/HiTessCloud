import os
import subprocess
from main import *
import os
import subprocess
from datetime import datetime

def AnalysisMongo(analysisType, user_id, user_name, user_company, user_dept, userFolder, runText, checkExtensionList):
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

    subprocess.Popen(runText, shell=True).wait()

    allFiles = os.listdir(userFolder)
    resultFileList = []

    for ext in checkExtensionList:
        matched = [f for f in allFiles if f.endswith(ext)]
        resultFileList.extend([os.path.join(userFolder, f) for f in matched])

    all_found = len(resultFileList) > 0
    status = "Complete" if all_found else "Error"

    mongo.db.analysis.update_one(
        {'_id': result.inserted_id},
        {
            '$set': {
                'status': status,
                'files': resultFileList
            }
        })


def TrussModelBuilderRun(programDirectory, receiveFile1, receiveFile2, userFolder, user_id, user_name, user_company, user_dept):
  try:
    programEXE = os.path.join(programDirectory, "TrussModelBuilder.exe")
    runText = f"{programEXE} {programDirectory} {receiveFile1} {receiveFile2}"

    AnalysisMongo('Truss 해석 모델 구축', user_id, user_name, user_company, user_dept, userFolder, runText, [".bdf"])

  except Exception as e:
      print("TrussModelBuilderRun 예외 발생:", e)


def TrussAssessmentRun(programDirectory, receiveFile, userFolder, user_id, user_name, user_company, user_dept):
  try:
    programEXE = os.path.join(programDirectory, "TrussAssessment.exe")
    runText = f"{programEXE} {receiveFile}"   

    AnalysisMongo('Truss 구조 해석', user_id, user_name, user_company, user_dept, userFolder, runText, [".xlsx", ".f06", ".op2"])

  except Exception as e:
      print("TrussAssessment 예외 발생:", e)
