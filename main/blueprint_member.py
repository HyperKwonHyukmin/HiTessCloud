from main import *
from flask import Blueprint, send_from_directory, jsonify
from .EmpIDValid import classEmpIDValid
from datetime import datetime
import os
from collections import defaultdict

def format_datetime(value):
  now_timestamp = time.time()
  offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
  value = datetime.fromtimestamp(int(value) / 1000) + offset
  return value.strftime('%Y-%m-%d %H:%M:%S')

# 사용자별 통계를 위한 딕셔너리 생성
def PersonalUserCounter(data):
    # 결과 딕셔너리 초기화
  result = {
      "year": defaultdict(lambda: defaultdict(int)),
      "month": defaultdict(lambda: defaultdict(int)),
      "week": defaultdict(lambda: defaultdict(int)),
      "day": defaultdict(lambda: defaultdict(int)),
  }
  # 데이터 처리
  for analysisType, analysisTime in data:
    # 날짜 변환
    dt = datetime.strptime(analysisTime, '%Y-%m-%d %H:%M:%S')
    
    # 연도별 집계
    year_key = str(dt.year)
    result["year"][year_key][analysisType] += 1
    
    # 월별 집계
    month_key = dt.strftime('%Y-%m')
    result["month"][month_key][analysisType] += 1
    
    # 주별 집계
    week_key = f"{dt.year}-W{dt.isocalendar().week:02}"
    result["week"][week_key][analysisType] += 1
    
    # 일별 집계
    day_key = dt.strftime('%Y-%m-%d')
    result["day"][day_key][analysisType] += 1

  # 결과 변환 (defaultdict를 dict로 변환)
  result = {key: {k: dict(v) for k, v in value.items()} for key, value in result.items()}
  return result

# member 페이지에 Bulueprint 사용
blueprint = Blueprint('member', __name__, url_prefix='/member')

## member login 라우터 ######################################################################################
@blueprint.route('/login', methods=['POST', 'GET'])
def member_login():
  if request.method == 'POST':
    userID = request.form.get('id')
    userID = userID.upper() # 사번의 소문자, 대문자 모두 사용하기 위함   
    company = request.form.get('company')
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

  else: # request.method가 GET이라면?
    next_url = request.args.get('next_url', type=str)
    if next_url is not None:
      return render_template('blockLogin.html', next_url=next_url, title='회원 로그인')
    else:
      return render_template('blockLogin.html', title='회원 로그인')


## member login API 라우터 ######################################################################################
@blueprint.route('/loginAPI', methods=['POST'])
def member_loginAPI():
    userID = request.form.get('id')
    userID = userID.upper() # 사번의 소문자, 대문자 모두 사용하기 위함
    company = request.form.get('company')
    members = mongo.db.members #PyMongo의 members Collections 불러오기
    data = members.find_one({'userID' : userID, 'userCompany' : company}) # 사번을 Key로 값 찾기
    if not data:
        return jsonify({
            "success": False,
            "reason": "not_found"
        })
    elif data.get('isMember') == 'False':
        return jsonify({
            "success": False,
            "reason": "no_member"
        })
    elif data.get('isMember') == 'True' and 'Beam Structure Solution' not in data.get('permissions', {}):
        return jsonify({
            "success": False,
            "reason": "no_permission"
        })
    else:
        return jsonify({
            "success": True,
            "userID": data.get("userID"),
            "userName": data.get("userName"),
            "userDept": data.get("userDept"),
            "userPos": data.get("userPos"),
            "userCompany": data.get("userCompany")
        })

## member logout 라우터 ######################################################################################
@blueprint.route('/logout')
def member_logout():
  try:
    del session['userID'] # 로그 아웃하면 생성하였던 session들을 모두 제거 한다. 
    del session['userName']
    del session['userCompany']
    del session['userDept']
    del session['userPos']
    del session['permissions']
  except:
    pass
  return redirect(url_for('member.member_login'))


## member 회원가입 라우터 ######################################################################################
@blueprint.route('/join', methods=['POST', 'GET'])
def member_join():
  if request.method == 'GET':
    return render_template('blockJoinBefore.html', title='회원가입')
  else:
    hidden = request.form.get('hidden') # hidden에 사번정보 확인 전인지, 아니면 후인지를 판단하도록 하였음
    id = request.form.get('id')

    if hidden == 'confirm': # 사번 확인 단계
      Val = classEmpIDValid() 
      try:                        
        Val.Search(id)
        userID = id
        userName = Val.userName
        userDept = Val.userDept
        userPos = Val.userPos
        userData = {
              'userID' : userID,
              'userName' : userName,
              'userDept' : userDept,
              'userPos' : userPos,
          }
        return render_template('blockJoinAfter.html', userData = userData, title='회원가입') 
      except:
        flash('사번 정보가 없습니다.')
        return render_template('blockJoinBefore.html', title='회원가입')

    else: # 사번 확인이 끝나고 회원 가입 단계
      Val = classEmpIDValid() 
      Val.Search(id)
      userID = id
      company = request.form.get('company')
      userID = userID.upper()
      userName = Val.userName
      userDept = Val.userDept
      userPos = Val.userPos
      current_utc_time = round(datetime.utcnow().timestamp() * 1000) # 회원 가입을 하는 시간 기록

      # 회원 가입 정보를 DB에 저장
      userData = {
            'userID' : userID, # 사번
            'userName' : userName, # 회원이름
            'userCompany' : company, # 회사이름
            'userDept' : userDept, # 회원부서
            'userPos' : userPos, # 회원직급
            'joinTime' : current_utc_time, # 회원가입 시간
            'joinCNT' : 0, # 회원로그인 횟수
            'analysisCNT' : 0, # 회원 프로그램 사용 횟수
            'isMember' : 'False', # 관리자 승인 유무
            'permissions' : {}
        }
      members = mongo.db.members
      cnt = members.count_documents({'userID' : userID}) # 이미 가입되어 있는 회원인지 확인
      if cnt > 0:
        flash('이미 회원입니다.')
        return render_template('blockJoinBefore.html', title='Join')
      members.insert_one(userData)      
      return render_template('index.html')

## API에서 회원정보 확인용 라우터 ##################################
@blueprint.route('/check_user', methods=['POST'])
def api_check_user():
    data = request.get_json(silent=True) or {}
    user_id = (data.get('userID') or '').upper()
    company = data.get('company')

    members = mongo.db.members
    user = members.find_one({"userID": user_id, "userCompany": company})

    if not user:
        return jsonify({"ok": False, "reason": "not_registered"}), 404
    if user.get('isMember') == 'False':
        return jsonify({"ok": False, "reason": "not_approved"}), 403

    return jsonify({
        "ok": True,
        "userName": user.get("userName"),
        "permissions": user.get("permissions", {})
    })


## HD 현대삼호 member 회원가입 라우터 ######################################################################################
@blueprint.route('/joinSamho', methods=['GET', 'POST'])
def member_join_samho():
  if request.method == 'GET':
    return render_template('blockJoinSamho.html', title='HD 현대삼호 회원가입')
  else:
    company = request.form.get('company')
    userID = request.form.get('id').upper()
    userName = request.form.get('name')
    userDept = request.form.get('division')
    userPos = request.form.get('rank')  # ← select로 넘어온 직급값
    current_utc_time = round(datetime.utcnow().timestamp() * 1000) # 회원 가입을 하는 시간 기록
    # 회원 가입 정보를 DB에 저장
    userData = {
          'userID' : userID, # 사번
          'userName' : userName, # 회원이름
          'userCompany' : company, # 회사이름
          'userDept' : userDept, # 회원부서
          'userPos' : userPos, # 회원직급
          'joinTime' : current_utc_time, # 회원가입 시간
          'joinCNT' : 0, # 회원로그인 횟수
          'analysisCNT' : 0, # 회원 프로그램 사용 횟수
          'isMember' : 'False', # 관리자 승인 유무
          'permissions' : {}
      }

    members = mongo.db.members
    cnt = members.count_documents({'userID' : userID}) # 이미 가입되어 있는 회원인지 확인
    if cnt > 0:
      flash('이미 회원입니다.')
      return render_template('blockJoinBefore.html', title='Join')

    members.insert_one(userData)
    return render_template('index.html')

## member MyPage 라우터 ######################################################################################
@blueprint.route('/mypage', methods=['GET', 'POST'])
@login_required
def member_mypage():
  members = mongo.db.members
  userData = members.find_one({'userID' : session['userID']}) # 현재 로그인 중인 회원의 DB정보 가지고 오기    
  userData_result = {
    'joinCNT' : userData.get('joinCNT'), # 회원로그인 횟수 
    'analysisCNT' : userData.get('analysisCNT'), # 회원 프로그램 사용 횟수
  }

  # 페이지네이션 설정 
  page = request.args.get('page', default=1, type=int)
  limit = request.args.get('limit', 10, type=int) # 한페이지에 10개의 정보 보여주기
  analysis = mongo.db.analysis
  analysisData = analysis.find({'userID':session['userID']}).sort('analysisTime',-1).skip((page-1) * limit).limit(limit)

  testAnalaysisData = list(analysis.find({'userID':session['userID']}).sort('analysisTime',-1))
  testAnalaysisData = [(item['analysisType'], format_datetime(item['analysisTime'])) for item in testAnalaysisData]

  userCounter_dict = PersonalUserCounter(testAnalaysisData)
 

 # POST 요청 처리 (JavaScript에서 데이터 요청 시)
  if request.method == 'POST':
    time_unit = request.json.get("time_unit")
    selected_time = request.json.get("selected_time")
    if selected_time is None:
        # 전체 데이터를 반환
        selected_data = userCounter_dict.get(time_unit, {})
    else:
        # 특정 시간 데이터를 반환
        selected_data = userCounter_dict.get(time_unit, {}).get(selected_time, {})
    
    return jsonify(selected_data)


  
  tot_count = analysis.count_documents({})
  last_page_num = math.ceil(tot_count / limit)
  block_size = 5 # 블록 5개만 하단에 표시하기 
  block_num = int((page - 1) / block_size)
  block_start = int((block_size * block_num) + 1)
  block_last = math.ceil(block_start + (block_size-1))
  return render_template('blockMypage.html', 
                          analysisData=list(analysisData),
                          limit = limit,
                          page = page,
                          block_start = block_start,
                          block_last = block_last,
                          last_page_num = last_page_num,
                          title='My page',
                          userData_result = userData_result)


## member MyPage의 해석결과 다운로드 받기 라우터 ######################################################################################
@blueprint.route('/filedownload/<fileName>')
@login_required
def download(fileName):
  # fileName = 'file1', 'file2', 'file3' 등
  file = request.args.get(fileName)  # 동적으로 해당 파라미터 받기

  if not file:
      return f"{fileName}에 해당하는 파일 경로가 없습니다.", 400

  folderName = os.path.dirname(file)
  pureFileName = os.path.basename(file)

  return send_from_directory(folderName, pureFileName, as_attachment=True)

## Program Access 라우터 ######################################################################################
@blueprint.route('/myAccess', methods = ['GET', 'POST'])
@login_required
def member_access():
    members = mongo.db.members

    # 최신 DB 값으로 session 갱신
    userData = members.find_one({'userID': session['userID']})
    session['permissions'] = userData.get('permissions', {})

    return render_template('blockAccess.html', title='Hi-TESS 프로그램 사용 권한 조회')



## 프로그램 사용권한 신청 라우터 ######################################################################################
@blueprint.route('/requestPermissions', methods=['POST'])
@login_required
def member_requestPermissions():
    members = mongo.db.members
    user_id = session['userID']
    program_name = request.form.get('program_name')  # 예: "Truss 해석 모델 구축"

    # 승인 없이 무조건 사용할수 있는 프로그램 목록
    autoPermission_program = ["Beam Structure Solution"]

    update_key = f"permissions.{program_name}"



    if program_name in autoPermission_program:
        members.update_one(
            {'userID': user_id},
            {'$set': {update_key: True}}
        )
    else:
        members.update_one(
            {'userID': user_id},
            {'$set': {update_key: False}}  # False = 신청중 상태
        )

    # 최신 권한 상태 세션에 반영
    userData = members.find_one({'userID': user_id})
    session['permissions'] = userData.get('permissions', {})

    flash(f"{program_name} 프로그램 사용권한을 신청하였습니다.", "success")

    return render_template('blockAccess.html', title='Hi-TESS 프로그램 사용 권한 조회', session=session)
