"""
Mast Post Assessment Blueprint (Full Integration Version)
"""
from flask import Blueprint, render_template, request, session, flash
import os
import subprocess
import threading
import json
import traceback
from .common import *
from .ProjectCodes import MastPost

blueprint = Blueprint('mastpost', __name__, url_prefix='/mastpost')
baseDirectory = r'C:\Users\HHI\KHM\HiTessCloud_Flask'

@blueprint.route('/mastpost', methods=['GET', 'POST'])
# @login_required
def mastpost_calculate():
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\MastPost")
    programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\PostMast")
    exe_path = os.path.join(programDirectory, "PostDavitCalculation.exe")

    if request.method == 'POST':

        userFolder = UserFolderCreate(userDirectory, request)
        post_height = request.form.get('postHeight', '4200')
        platform_weight = request.form.get('platformWeight', '150')

        user_id = session.get('userID', 'test_user')
        user_name = session.get('userName', 'test_name')
        user_company = session.get('userCompany', 'test_company')
        user_dept = session.get('userDept', 'test_dept')

        try:
            # 2. C# 엔진에 전달할 3개의 인자 구성
            cmd_args = [
                exe_path,
                str(userFolder),
                str(post_height),
                str(platform_weight)
            ]

            # 3. C# 실행 및 텍스트 캡처
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            # 4. 브라우저에 원시 결과(Raw Result)만 직관적으로 표출 (JSON 파싱 제외)
            html_response = f"""
                    <div style="padding: 50px; font-family: 'Noto Sans KR', sans-serif;">
                        <h2 style="color: #002b5c;">✅ C# 엔진 실행 테스트 (인자 3개 연동)</h2>
                        <hr style="margin-bottom: 20px;">
                        <ul style="font-size: 18px; line-height: 1.8;">
                            <li><strong>1. userFolder :</strong> {userFolder}</li>
                            <li><strong>2. Post Height :</strong> <span style="color: red;">{post_height}</span></li>
                            <li><strong>3. Platform Weight :</strong> <span style="color: blue;">{platform_weight}</span></li>
                        </ul>

                        <div style="margin-top: 30px; background-color: #f8f9fa; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                            <h3 style="margin-top:0;">🤖 엔진(PostDavitCalculation.exe) 응답 결과</h3>

                            <p><strong>✅ 표준 출력 (stdout) - 정상 로그 또는 JSON 문자열:</strong></p>
                            <pre style="background:#fff; padding:15px; border:1px solid #ccc; overflow-x: auto;">{result.stdout if result.stdout.strip() else "출력값 없음"}</pre>

                            <p style="color: red; margin-top: 20px;"><strong>🚨 에러 로그 (stderr) - 에러 발생 시:</strong></p>
                            <pre style="background:#fff; padding:15px; border:1px solid #f5c6cb; color: #721c24; overflow-x: auto;">{result.stderr if result.stderr.strip() else "에러 없음"}</pre>
                        </div>

                        <br><br>
                        <button onclick="history.back()" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">뒤로 가기</button>
                    </div>
                    """
            return html_response

        except Exception as e:
            print(f"[Python Error] {traceback.format_exc()}")
            flash(f"해석 엔진 실행 실패: {str(e)}")
            return render_template('blockMastPost.html', title='Hi-TESS Mast Post', calculated=False)

    else:
        # GET 요청 (초기 접속)
        return render_template('blockMastPost.html', title='Mast & Post Design', calculated=False)