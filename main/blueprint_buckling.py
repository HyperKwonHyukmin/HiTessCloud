from main import *
from flask import Blueprint, render_template, request, session, flash
import os
import subprocess
import re
from .ProjectCodes import Buckling

# 프로젝트 폴더 설정 (기존 blueprint_beam.py와 동일하게 세팅)
baseDirectory = r'C:\Users\HHI\KHM\HiTessCloud_Flask'

# Buckling Analysis 페이지에 사용할 Blueprint 생성
blueprint = Blueprint('buckling', __name__, url_prefix='/buckling')


## 기둥 좌굴 계산 라우터 ######################################################################################
@blueprint.route('/columnbuckling', methods=['GET', 'POST'])
@login_required
def buckling_calculate():
    # C# 실행 파일(.exe)이 있는 경로 설정 (실제 경로에 맞게 수정 필요)
    programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\Buckling")
    exe_path = os.path.join(programDirectory, "ColumnBucklingApp.exe")

    if request.method == 'POST':
        # 1. 프론트엔드(HTML)에서 전송한 폼 데이터(Input) 받기
        safety_factor = request.form.get('safetyFactor', '3.0')
        member_select = request.form.get('memberSelect')
        material = request.form.get('material')
        length = request.form.get('length')
        eccentricity = request.form.get('eccentricity')

        user_id = session['userID']
        user_name = session['userName']
        user_company = session['userCompany']
        user_dept = session['userDept']

        try:
            # 1. 혹시 모를 None 값을 방지하기 위해 모든 인자를 안전하게 문자열(str)로 캐스팅
            cmd_args = [
                exe_path,
                str(member_select),
                str(length),
                str(eccentricity)
            ]

            # 2. subprocess로 C# 콘솔 프로그램 호출 (방어 옵션 추가)
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                encoding='cp949',  # 윈도우 환경에서 파싱 에러가 계속 나면 'cp949'로 변경하세요!
                errors='replace'  # 글자가 깨져도 프로그램이 죽지 않도록 방어
            )

            # 3. stdout이 None일 경우 빈 문자열("")로 대체하여 정규식(TypeError) 에러 원천 차단
            output = result.stdout if result.stdout else ""

            # 4. 정규 표현식(Regex)을 사용하여 C# 출력 텍스트에서 결과값 추출
            area_match = re.search(r'- 단면적\(A\)\s*:\s*([0-9\.]+)', output)
            inertia_match = re.search(r'- 관성모멘트\(I\)\s*:\s*([0-9\.]+)', output)
            radius_match = re.search(r'- 회전반경\(r\)\s*:\s*([0-9\.]+)', output)
            modulus_match = re.search(r'- 단면계수\(Z\)\s*:\s*([0-9\.]+)', output)
            elastic_match = re.search(r'- 탄성계수\(E\)\s*:\s*([0-9\.]+)', output)
            yield_match = re.search(r'- 항복응력\(Fy\)\s*:\s*([0-9\.]+)', output)
            load_match = re.search(r'=> 최대 허용 사용하중\s*:\s*([0-9\.]+)', output)
            ecc_match = re.search(r'- 편심 비율\(%\)\s*:\s*([0-9\.]+)', output)
            load_match = re.search(r'=> 최대 허용 사용하중\s*:\s*([0-9\.]+)', output)

            # 5. C#이 성공적으로 하중 결과값을 뱉었을 경우
            if load_match:
                member_area = area_match.group(1) if area_match else "-"
                member_inertia = inertia_match.group(1) if inertia_match else "-"
                member_radius = radius_match.group(1) if radius_match else "-"
                member_modulus = modulus_match.group(1) if modulus_match else "-"
                member_elastic = elastic_match.group(1) if elastic_match else "-"
                member_yield = yield_match.group(1) if yield_match else "-"
                member_eccentricity = ecc_match.group(1) if ecc_match else eccentricity
                safe_load = load_match.group(1)

                thread = threading.Thread(
                    target=Buckling.ColumnBucklingAssessmentRun,
                    args=(programDirectory, user_id, user_name, user_company,user_dept))
                thread.start()

                return render_template(
                    'blockColumnBuckling.html',  # 실제 HTML 파일명(대소문자)과 똑같이 맞춰주세요!
                    title='Hi-TESS Column Buckling',
                    calculated=True,
                    member_name=member_select,
                    member_area=member_area,
                    member_inertia=member_inertia,
                    member_radius=member_radius,
                    member_modulus=member_modulus,
                    member_elastic=member_elastic,
                    member_yield=member_yield,
                    member_length=length,
                    member_eccentricity=member_eccentricity,
                    safe_load=safe_load
                )
            else:
                # C# 결괏값 도출 실패 시 로그에 C# 에러 메시지 표출
                error_msg = result.stderr if result.stderr else output
                print(f"[C# Engine Error] {error_msg}")
                flash("C# 계산 엔진에서 결과값을 도출하지 못했습니다. 서버 콘솔 창을 확인하세요.")
                return render_template('blockColumnBuckling.html', title='Hi-TESS Column Buckling', calculated=False)

        except Exception as e:
            print(f"[Python Error] {str(e)}")
            flash(f"해석 엔진 실행 실패: {str(e)}")
            return render_template('blockColumnBuckling.html', title='Hi-TESS Column Buckling', calculated=False)

    else:
        # GET 요청 (최초 페이지 접속 시)
        user_permissions = session.get('permissions', {})
        programName = "기둥 좌굴 해석"  # 권한 DB에 등록된 명칭으로 수정

        # 권한 체크 (beam의 로직 차용)
        # if programName in user_permissions and user_permissions[programName] == True:
        return render_template('BlockColumnBuckling.html', title='Hi-TESS Column Buckling', calculated=False)
        # else:
        #     flash("프로그램 권한 신청이 필요합니다.")
        #     return redirect(url_for('index')) # root 페이지로 리다이렉트