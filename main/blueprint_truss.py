from main import *
from flask import Blueprint, send_from_directory
import os
import threading
from .common import *
from .ProjectCodes import Truss


# 프로젝트 폴더 설정
# baseDirectory = r'C:\Coding\Web\Project\HiTessCloud_Flask'
# 연구실 서버용
baseDirectory = r'C:\Users\HHI\KHM\HiTessCloud_Flask'

# Truss Analysis 페이지에 Bulueprint 사용
blueprint = Blueprint('truss', __name__, url_prefix='/truss')

## trussIntro 라우터 ######################################################################################
@blueprint.route('/intro')
@login_required
def truss_intro():
  members = mongo.db.members
  userData = members.find_one({'userID': session['userID']})
  session['permissions'] = userData.get('permissions', {})
  return render_template('blockTrussIntro.html', title='Truss 해석 기능 소개')


## trussModelBuilder 라우터 ######################################################################################
@blueprint.route('/trussModelBuilder', methods = ['GET', 'POST'])
@login_required
def TrussModelBuilder():
  userDirectory = os.path.join(baseDirectory, r"main\userConnection\Truss\TrussModelBuilder")
  programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\Truss\TrussModelBuilder")
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
            target=Truss.TrussModelBuilderRun,
            args=(programDirectory, receiveFile1, receiveFile2, userFolder, user_id, user_name, user_company, user_dept))
    thread.start()
    return render_template('blockTrussModelBuilder.html', title='Hi-TESS Truss')
  else:
    user_permissions = session['permissions']
    programName = "Truss 해석 모델 구축"
    if programName in user_permissions and user_permissions[programName] == True:
      return render_template('blockTrussModelBuilder.html', title='Hi-TESS Truss')
    else:
      flash(f"프로그램 권한 신청이 필요합니다.")
      return render_template('index.html', title='Hi-TESS CLOUD')

## trussAssessment 라우터 ######################################################################################
@blueprint.route('/trussAssessment', methods = ['GET', 'POST'])
@login_required
def TrussAssessment():
  userDirectory = os.path.join(baseDirectory, r"main\userConnection\Truss\TrussAssessment")
  programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\Truss\TrussAssessment")
  if request.method == 'POST':
    userFolder = UserFolderCreate(userDirectory, request)
    receiveFile1 = ReceiveFileSave(userFolder, 'file1', request)
    user_id = session['userID']
    user_name = session['userName']
    user_company = session['userCompany']    
    user_dept = session['userDept']
    flash(f"해석 결과는 My page에서 확인하세요")
    thread = threading.Thread(
            target=Truss.TrussAssessmentRun,
            args=(programDirectory, receiveFile1, userFolder, user_id, user_name, user_company, user_dept))
    thread.start()
    return render_template('blockTrussAssessment.html', title='Hi-TESS Truss')
  else:
    user_permissions = session['permissions']
    programName = "Truss 구조 안정성 평가"
    if programName in user_permissions and user_permissions[programName] == True:
      return render_template('blockTrussAssessment.html', title='Hi-TESS Truss')
    else:
      flash(f"프로그램 권한 신청이 필요합니다.")
      return render_template('index.html', title='Hi-TESS CLOUD')




# @blueprint.route('/trussAnalysis', methods = ['GET', 'POST'])
# @login_required
# def TrussAnalysis():
#   if request.method == 'POST':
#     ip_address = str(request.remote_addr)
#     current_utc_time = str(round(datetime.utcnow().timestamp() * 1000))
#     user_folder = ip_address + '_' + current_utc_time
#     os.chdir(userDirectory)
#     save_path = os.path.join(userDirectory, user_folder)
#     os.mkdir(save_path)
#     f = request.files['file']
#     bdf_file = os.path.join(save_path, f.filename)
#     f.save(bdf_file)

#     try:   
#       future = Nastran_Thread(bdf_file)
#       EF_Result, list_EF_Summary, Leg_distribution_panel = future.result()

#       result = {
#         'EF_Result' : EF_Result,
#         'list_EF_Summary' : list_EF_Summary,
#         'Leg_distribution_panel' : Leg_distribution_panel,
#       }

#       analysisData = Truss_log_save('Truss / Leg Lifting 구조검토 ',bdf_file)

#       return render_template('truss_global_result.html', result=result, analysisData=analysisData, title='Truss / Leg Lifting 구조해석 프로그램') 

#     except:
#       error_file = os.path.join(save_path,'Error.txt')        

#       with open(error_file, 'r', encoding='utf8') as f:
#         log_text = f.readlines()    
      
#       log_text = [i.strip() for i in log_text]

#       log_text_flash = ''
#       for i in log_text:
#         log_text_flash = log_text_flash + i + ' '      

#       print('log_text_flash : ', log_text_flash)  
#       flash(log_text_flash)
#       return render_template('blockTrussAnalysis.html', title='Truss / Leg Lifting 구조해석 프로그램')
#   else:
#     return render_template('blockTrussAnalysis.html', title='Truss / Leg Lifting 구조해석 프로그램')

# Truss 해석 결과 파일 다운로드 
@blueprint.route('/trussGlobal_filedownload', methods = ['GET', 'POST'])
@login_required
def global_download():
  file = request.args.get('file')
  folderName = os.path.dirname(file)
  fileName = file.split('\\')[-1]

  return send_from_directory(folderName, fileName, as_attachment=True)


 ## Truss Lifting Analysis 라우터 ######################################################################################
# @blueprint.route('/trussLifting')
# @login_required
# def truss_lifting():
#   return render_template('truss_lifting.html', title='Truss Module Lifting 구조해석 프로그램')

# @blueprint.route('/trussLifting_analysis', methods = ['GET', 'POST'])
# @login_required
# def trussLifting_upload():
#   if request.method == 'POST':
#     ip_address = str(request.remote_addr)
#     current_utc_time = str(round(datetime.utcnow().timestamp() * 1000))
#     user_folder = ip_address + '_' + current_utc_time
#     os.chdir(userDirectory)
#     save_path = os.path.join(userDirectory, user_folder)
#     os.mkdir(save_path)

#     f_Node = request.files['Node_file']
#     f_Way = request.files['Way_file']
#     f_LOADSPC = request.files['LOADSPC_file']
#     Node_file = os.path.join(save_path, f_Node.filename)
#     Way_file = os.path.join(save_path, f_Way.filename)
#     LOADSPC_file = os.path.join(save_path, f_LOADSPC.filename)
#     f_Node.save(Node_file)
#     f_Way.save(Way_file)
#     f_LOADSPC.save(LOADSPC_file)

#     try:
#       future = Nastran_Thread_Lifting(Node_file, Way_file, LOADSPC_file, code_path)
#       list_assessment, result_assessment = future.result()

#       result = {
#         'list_assessment' : list_assessment,
#         'result_assessment' : result_assessment
#       }

#       bdf_file = os.path.join(save_path, 'Truss_Lifting_Model.bdf')

#       analysisData = Truss_log_save('Truss / Leg Lifting 구조검토 ',bdf_file)

#       return render_template('truss_lifting_result.html', result=result, analysisData=analysisData, title='Truss Module Lifting 구조해석 프로그램') 

#     except:
#       error_file = os.path.join(save_path,'Error.txt')        

#       with open(error_file, 'r', encoding='utf8') as f:
#         log_text = f.readlines()    
      
#       log_text = [i.strip() for i in log_text]

#       log_text_flash = ''
#       for i in log_text:
#         log_text_flash = log_text_flash + i + ' '      

#       print('log_text_flash : ', log_text_flash)  
#       flash(log_text_flash)
#       return render_template('truss_lifting.html', title='Truss Module Lifting 구조해석 프로그램')

# # Truss Module Lifting 해석 결과 파일 다운로드 
# @blueprint.route('/trussLifting_filedownload', methods = ['GET', 'POST'])
# @login_required
# def lifting_download():
#   file = request.args.get('file')
#   folderName = os.path.dirname(file)
#   fileName = file.split('\\')[-1]

#   return send_from_directory(folderName, fileName, as_attachment=True)

    # try:   
    #   future = Nastran_Thread(bdf_file)
    #   EF_Result, list_EF_Summary, Leg_distribution_panel = future.result()

    #   result = {
    #     'EF_Result' : EF_Result,
    #     'list_EF_Summary' : list_EF_Summary,
    #     'Leg_distribution_panel' : Leg_distribution_panel,
    #   }

    #   analysisData = Truss_log_save('Truss / Leg Lifting 구조검토 ',bdf_file)

    #   return render_template('truss_global_result.html', result=result, analysisData=analysisData, title='Truss / Leg Lifting 구조해석 프로그램') 

    # except:
    #   error_file = os.path.join(save_path,'Error.txt')        

    #   with open(error_file, 'r', encoding='utf8') as f:
    #     log_text = f.readlines()    
      
    #   log_text = [i.strip() for i in log_text]

    #   log_text_flash = ''
    #   for i in log_text:
    #     log_text_flash = log_text_flash + i + ' '      

    #   print('log_text_flash : ', log_text_flash)  
    #   flash(log_text_flash)
    #   return render_template('truss_global.html', title='Truss / Leg Lifting 구조해석 프로그램')

