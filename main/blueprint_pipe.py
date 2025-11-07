from main import *
from flask import Blueprint, send_from_directory
import os
import threading
from .common import *
from .ProjectCodes import Pipe

# 내 컴퓨터
# baseDirectory = r'C:\Coding\Web\Project\HiTessCloud_Flask'
# 연구실 서버
baseDirectory = r'C:\Users\HHI\KHM\HiTessCloud_Flask'
is_license_in_use = False

# Truss Analysis 페이지에 Bulueprint 사용
blueprint = Blueprint('pipe', __name__, url_prefix='/pipe')
# 전역 상태 플래그 선언 (파일 상단 또는 별도 상태 관리 모듈에서)



## Pipe Intro 라우터 ######################################################################################
@blueprint.route('/intro', methods=['GET', 'POST'])
@login_required
def pipe_intro():
    members = mongo.db.members
    userData = members.find_one({'userID': session['userID']})
    session['permissions'] = userData.get('permissions', {})
    return render_template('blockPipeIntro.html', title='Pipe 해석 기능 소개')


## FuelLine 라우터 ######################################################################################
@blueprint.route('/FuelLine', methods=['GET', 'POST'])
@login_required
def FuelLine():
    global is_license_in_use  # ← 여기 추가
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\PSA\FuelLine")
    programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\PSA\FuelLine")

    if request.method == "POST":
        if is_license_in_use:
            flash("⚠ 현재 프로그램이 사용 중입니다. 해석이 끝날 때까지 기다려 주세요.")
            return render_template('blockFuelLine.html', title='PSA / Fuel Line 배관 해석 프로그램', is_locked=True)
        is_license_in_use = True  # 사용 시작 표시
        userFolder = UserFolderCreate(userDirectory, request)
        receiveFile = ReceiveFileSave(userFolder, 'file1', request)
        user_id = session['userID']
        user_name = session['userName']
        user_company = session['userCompany']
        user_dept = session['userDept']

        def run_and_release():
            try:
                Pipe.run_analysis_background(programDirectory, receiveFile, userFolder, user_id, user_name,
                                             user_company, user_dept)
            finally:
                global is_license_in_use
                is_license_in_use = False  # 해석 완료 후 사용 종료

        threading.Thread(target=run_and_release).start()

        flash(f"해석 결과는 My page에서 확인하세요")
        return render_template('blockFuelLine.html', title='PSA / Fuel Line 배관 해석 프로그램')
    else:
        return render_template(
            'blockFuelLine.html',
            title='PSA / Fuel Line 배관 해석 프로그램',
            is_locked=is_license_in_use  # ← 이 줄이 중요
        )





