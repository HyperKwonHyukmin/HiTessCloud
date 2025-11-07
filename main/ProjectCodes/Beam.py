import os
import subprocess
from main import *
import os
import subprocess
from datetime import datetime

def AnalysisMongo(analysisType, user_id, user_name, user_company, user_dept,
                  userFolder = None, runText = None, checkExtensionList = None):
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
  if not runText: #runText 없으면 status를 None으로 지정
      analysisData['status'] = "None"
  result = mongo.db.analysis.insert_one(analysisData)


  if runText:
      # 명령어 실행
      subprocess.Popen(runText, shell=True).wait()  # shell=True 추가 (필요 시)

  if userFolder:
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

def MooringFittingRun(programDirectory, receiveFile1, receiveFile2, userFolder, user_id, user_name, user_company, user_dept):
  try:
    programEXE = os.path.join(programDirectory, "MooringFitting.exe")
    runText = f"{programEXE} {receiveFile1} {receiveFile2} {programDirectory}"

    AnalysisMongo('Mooring Fitting 구조 안정성 평가', user_id, user_name, user_company, user_dept, userFolder, runText, [".xlsx"])

  except Exception as e:
      print("Mooring Fitting 구조 안정성 평가 예외 발생:", e)



def BeamStructureSolutionRun(user_id, user_name, user_company, user_dept):
    AnalysisMongo('HiTESS Beam 구조해석', user_id, user_name, user_company, user_dept, runText=None)

