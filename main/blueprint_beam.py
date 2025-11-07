from main import *
from flask import Blueprint, send_from_directory
import os
import threading
from .common import *
from .ProjectCodes import Beam


# 프로젝트 폴더 설정
# baseDirectory = r'C:\Coding\Web\Project\HiTessCloud_Flask'
# 연구실 서버용
baseDirectory = r'C:\Users\HHI\KHM\HiTessCloud_Flask'

# Beam Analysis 페이지에 Bulueprint 사용
blueprint = Blueprint('beam', __name__, url_prefix='/beam')

## beamIntro 라우터 ######################################################################################
@blueprint.route('/intro')
@login_required
def beam_intro():
  members = mongo.db.members
  userData = members.find_one({'userID': session['userID']})
  session['permissions'] = userData.get('permissions', {})
  return render_template('blockBeamIntro.html', title='Beam 해석 기능 소개')


## MooringFitting 라우터 ######################################################################################
@blueprint.route('/mooringFitting', methods = ['GET', 'POST'])
@login_required
def MooringFitting():
  userDirectory = os.path.join(baseDirectory, r"main\userConnection\Beam\MooringFittingAssessment")
  programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\Beam\MooringFittingAssessment")
  if request.method == 'POST':
    userFolder = UserFolderCreate(userDirectory, request)
    receiveFile1 = ReceiveFileSave(userFolder, 'file1', request)
    receiveFile2 = ReceiveFileSave(userFolder, 'file2', request)
    user_id = session['userID']
    user_name = session['userName']
    user_company = session['userCompany']    
    user_dept = session['userDept']
    flash(f"해석 결과는 My page에서 확인하세요")
    thread = threading.Thread(
            target=Beam.MooringFittingRun,
            args=(programDirectory, receiveFile1, receiveFile2, userFolder, user_id, user_name, user_company, user_dept))
    thread.start()
    return render_template('blockMooringFittingAssessment.html', title='Hi-TESS MooringFitting')
  else:
    user_permissions = session['permissions']
    programName = "Mooring Fitting 구조 안정성 평가"
    if programName in user_permissions and user_permissions[programName] == True:
      return render_template('blockMooringFittingAssessment.html', title='Hi-TESS MooringFitting')
    else:
      flash(f"프로그램 권한 신청이 필요합니다.")
      return render_template('index.html', title='Hi-TESS CLOUD')



# Truss 해석 결과 파일 다운로드 
@blueprint.route('/trussGlobal_filedownload', methods = ['GET', 'POST'])
@login_required
def global_download():
  file = request.args.get('file')
  folderName = os.path.dirname(file)
  fileName = file.split('\\')[-1]

  return send_from_directory(folderName, fileName, as_attachment=True)

