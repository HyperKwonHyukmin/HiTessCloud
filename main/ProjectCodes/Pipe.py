import os
import subprocess
from main import *
import os
import subprocess
from datetime import datetime


def run_analysis_background(programDirectory, receiveFile1, userFolder, user_id, user_name, user_company, user_dept):
    try:
        pyFile = os.path.join(programDirectory, "PSAFuelLine.py")
        runText = f"python {pyFile} {receiveFile1}"

        # 분석 정보 MongoDB에 기록
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        analysisData = {
            'userID': user_id,
            'userName': user_name,
            'userCompany': user_company,
            'userDept': user_dept,
            'analysisType': 'Double Walled Fuel Line 배관 해석',
            'analysisTime': current_utc_time,
            'status': "Running",
            'files': []
        }
        mongo.db.members.find_one_and_update({'userID': user_id}, {"$inc": {"analysisCNT": 1}})
        result = mongo.db.analysis.insert_one(analysisData)

        # 해석 subprocess 실행
        process = subprocess.Popen(runText, shell=True)
        process.wait()  # 여기서 기다림 (근데 Flask 메인 쓰레드에 영향 없음)

        # 결과 파일 검사
        allFiles = os.listdir(userFolder)
        resultFileList = []
        all_found = True
        checkExtensionList = [".xlsx", ".bdf", ".f06"]

        for ext in checkExtensionList:
            matched = [f for f in allFiles if f.endswith(ext)]
            if matched:
                resultFileList.extend([os.path.join(userFolder, f) for f in matched])
            else:
                all_found = False

        status = "Complete" if all_found else "Error"

        # MongoDB에 최종 결과 업데이트
        mongo.db.analysis.update_one(
            {'_id': result.inserted_id},
            {
                '$set': {
                    'status': status,
                    'files': resultFileList
                }
            }
        )

    except Exception as e:
        print("Double Walled Fuel Line 배관 해석 예외 발생:", e)

# def AnalysisMongo(analysisType, user_id, user_name, user_company, user_dept, userFolder, runText, checkExtensionList):
#   current_utc_time = round(datetime.utcnow().timestamp() * 1000)
#   analysisData = {
#     'userID': user_id,
#     'userName': user_name,
#     'userCompany': user_company,
#     'userDept': user_dept,
#     'analysisType': analysisType,
#     'analysisTime': current_utc_time,
#     'status': "Running",
#     'files': []
#   }

#   mongo.db.members.find_one_and_update({'userID': user_id}, {"$inc": {"analysisCNT": 1}})
#   result = mongo.db.analysis.insert_one(analysisData)

#   # 명령어 실행
#   subprocess.Popen(runText, shell=True).wait()  # shell=True 추가 (필요 시)

#   allFiles = os.listdir(userFolder)
#   resultFileList = []
#   all_found = True

#   for ext in checkExtensionList:
#     matched = [f for f in allFiles if f.endswith(ext)]
#   if matched:
#     resultFileList.extend([os.path.join(userFolder, f) for f in matched])
#   else:
#     all_found = False

#   status = "Complete" if all_found else "Error"

#   mongo.db.analysis.update_one(
#       {'_id': result.inserted_id},
#       {
#           '$set': {
#               'status': status,
#               'files': resultFileList
#           }
#       })

# def PSADuelFuel(programDirectory, receiveFile1, userFolder, user_id, user_name, user_company, user_dept):
#   try:
#     pyFile = os.path.join(programDirectory, "PSAFuelLine.py")
#     runText = f"python {pyFile} {receiveFile1}"

#     AnalysisMongo('Double Walled Fuel Line 배관 해석', user_id, user_name, user_company, user_dept, userFolder, runText, [".xlsx", ".bdf", ".f06"])

#   except Exception as e:
#       print("Double Walled Fuel Line 배관 해석 예외 발생:", e)



