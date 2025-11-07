from main import *
from flask import Blueprint, send_from_directory

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/HiTESSShortCut', methods=['POST', 'GET'])
def shortCut():
  def to_upper_only_letters(s):
    return ''.join(char.upper() if char.isalpha() else char for char in s)
  userID = to_upper_only_letters(request.args.get('id'))
  company = request.args.get('company')     # URL에서 company 파라미터 추출
  if company == "HHI":
      company = "HD 현대중공업"
  elif company == "HSHI":
      company = "HD 현대삼호"       

  next_url = request.form.get('next_url')
  members = mongo.db.members #PyMongo의 members Collections 불러오기 
  data = members.find_one({'userID' : userID, 'userCompany' : company}) # 사번을 Key로 값 찾기
  if not data: # 사번에 DB에 없다면?
    flash('회원정보가 없습니다.')
    return redirect(url_for('member.member_login'))
  elif data.get('isMember') == 'False': # 해당 사번이 관리자 승인이 되어 있지 않다면?      
    flash('관리자 승인 필요 - 선박의장연구실 권혁민 책임 (3-6465)')
    return redirect(url_for('member.member_login'))
  else:
    data = members.find_one_and_update({'userID' : userID}, {"$inc" : {"joinCNT":1}}) # 로그인 할 때마다, 로그인 회수 1씩 증가 시키기   
    session['userID'] = userID # 해당 회원의 정보로 session을 생성한다. 
    session['userName'] = data.get('userName')
    session['userCompany'] = data.get('userCompany')
    session['userDept'] = data.get('userDept')
    session['userPos'] = data.get('userPos')      
    session['permissions'] = data.get('permissions')
    session.permanent = True # 세션 시간을 사용하기 위함
    if next_url is not None: # next_url은 로그인 페이지로 넘어가기 전 페이지를 기억해두고, 로그인 후 돌아간다. 
      return redirect(next_url)
    else:
      return render_template('index.html')

@app.route('/HiTESSShortCut/download', methods=['GET', 'POST'])
def shortCutDownload():
  # EXE 파일 경로 설정
  # 내컴퓨터
  # exe_directory = r'C:\Coding\Web\Project\HiTessCloud_Flask\main\EngineeringPrograms\HiTessShortCut'
  # 서버 컴퓨터
  exe_directory = r'C:\Users\HHI\KHM\HiTessCloud_Flask\main\EngineeringPrograms\HiTessShortCut'
  exe_filename = "HiTESSCloudShortCut.zip"  # 다운로드 시킬 EXE 파일명

  # 파일이 존재하는지 검증
  if not os.path.exists(os.path.join(exe_directory, exe_filename)):
      return jsonify({"error": "파일을 찾을 수 없습니다."}), 404

  # EXE 파일 다운로드 시도
  return send_from_directory(directory=exe_directory, path=exe_filename, as_attachment=True)