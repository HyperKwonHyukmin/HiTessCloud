from main import *
from flask import Blueprint, send_from_directory, jsonify, send_file
import os
import pickle, inspect, re
import threading
from .common import *
from werkzeug.utils import secure_filename
import subprocess
from .PythonModule.HookTrolley import HookTrolley
from .PythonModule.BdfToCsv import BdfToCsv
import traceback
from .ProjectCodes import Beam
from .ProjectCodes import HiTESS_Beam



# 내컴퓨터 폴더 설정
# baseDirectory = r'C:\Coding\Web\Project\HiTessCloud_Flask'
# 연구실 서버용
baseDirectory = r'C:\Users\HHI\KHM\HiTessCloud_Flask'

# HiTESS Bulueprint
blueprint = Blueprint('hitessbeam', __name__, url_prefix='/hitessbeam')


## csvToBdf 라우터 ######################################################################################
@blueprint.route('/csvToBdf', methods=['GET', 'POST'])

def CsvToBdf():
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\CsvToBdf")
    programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\HiTessBeam\CsvToBdf")
    try:
        # 1. 사용자 폴더 생성
        userFolder = UserFolderCreate(userDirectory, request)
        # print("userFolder:", userFolder)

        # 2. 업로드 파일 저장
        file_objects = request.files.getlist('file')
        saved_files = []
        pickle_path = None

        members = mongo.db.members

        user_id = request.form.get("userID", "").strip()
        if not user_id:
            return jsonify({"error": "userID is required"}), 400

        data = (mongo.db.members.find_one({'userID': user_id}) or {})
        userName = data.get('userName', '')
        userCompany = data.get('userCompany', '')
        userDept = data.get('userDept', '')

        # print("[CsvToBdf] userID =", request.form.get("userID"))
        # print("[CsvToBdf] files count =", len(request.files.getlist('file')))
        # print("[CsvToBdf] names =", [f.filename for f in request.files.getlist('file')])

        HiTESS_Beam.CsvToBdfRun(user_id, userName, userCompany, userDept)

        for f in file_objects:
            filename = secure_filename(f.filename)
            save_path = os.path.join(userFolder, filename)
            f.save(save_path)
            saved_files.append(save_path)
            if filename.endswith('.pkl'):
                pickle_path = save_path

        if not pickle_path:
            return jsonify({"error": "input.pkl not found"}), 400

        # pickle 찾은 뒤
        # print("[CsvToBdf] pickle_path =", pickle_path)

        # 3. input.pkl 로부터 역할 파악
        with open(pickle_path, 'rb') as pf:
            original_list = pickle.load(pf)  # ['stru.csv', 'None', 'equi.csv']

        role_files = {'stru': None, 'pipe': None, 'equi': None}
        for i, key in enumerate(role_files.keys()):
            if original_list[i] and original_list[i].lower() != 'none':
                filename_only = os.path.basename(original_list[i])
                matching = next((f for f in saved_files if os.path.basename(f) == filename_only), None)
                if matching:
                    role_files[key] = matching

        if not role_files['stru']:
            return jsonify({"error": "Structural CSV file is required"}), 400

        # 매핑 완료 후
        print("[CsvToBdf] role_files =", role_files)

        def run_CsvToBdf(programDirectory, stru_file, pipe_file, equi_file, userFolder):
            # exe_path = os.path.join(programDirectory, "CsvToBdf.exe") # 구버전
            exe_path = os.path.join(programDirectory, "CsvToBdf_HiTESS.exe")
            csvFileName = os.path.basename(stru_file)
            bdfFileName = csvFileName.replace(".csv", ".bdf")
            bdf_file = os.path.join(userFolder, bdfFileName)

            input_list = [
                stru_file if stru_file else "None",
                pipe_file if pipe_file else "None",
                equi_file if equi_file else "None"
            ]

            runText = f'"{exe_path}" "{input_list[0]}" "{input_list[1]}" "{input_list[2]}" "{bdf_file}"'
            print("runText : ", runText)

            subprocess.Popen(runText).wait()

            return bdf_file

        # 스레드 제거 → 그냥 run_analysis() 직접 호출
        bdf_file = run_CsvToBdf(
            programDirectory,
            role_files['stru'],
            role_files['pipe'],
            role_files['equi'],
            userFolder
        )

        # 생성 성공 여부 확인
        if not bdf_file or not os.path.exists(bdf_file):
            return jsonify({"error": "BDF 파일 생성 실패"}), 500

        # 응답 준비
        folder_name_only = os.path.basename(userFolder)
        bdf_filename = os.path.basename(bdf_file)

        return jsonify({
            "message": "서버에서 BDF 변환이 완료되었습니다.",
            "userFolder": folder_name_only,
            "bdfFilename": bdf_filename
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## BeamStructureAnalysis 라우터 ######################################################################################
@blueprint.route('/beamStructureAnalysis', methods=['POST'])
def BeamStructureAnalysis():
    # ──[원래 경로 유지]──────────────────────────────────────────
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\BeamStructureAnalysis")
    os.makedirs(userDirectory, exist_ok=True)

    # userID 간단 검증(영/숫/언더/대시 1~64자) — 형식만 체크
    USERID_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")

    def extract_user_id(req) -> str:
        user_id = ""
        if req.is_json:
            user_id = (req.get_json(silent=True) or {}).get("userID", "") or ""
        if not user_id:
            user_id = req.form.get("userID", "") or ""
        return user_id.strip()

    # BeamStructureSolutionRun 시그니처 호환 래퍼
    def run_beam_solution(user_folder: str, user_id: str):
        fn = getattr(Beam, "BeamStructureSolutionRun", None)
        if fn is None:
            return "BeamStructureSolutionRun not found in Beam module"
        sig = inspect.signature(fn)
        try:
            # (userFolder, userID) 먼저 시도
            return fn(user_folder, user_id)
        except TypeError:
            try:
                # (userFolder, userID, userName, userCompany, userDept) 호환
                return fn(user_folder, user_id, "", "", "")
            except TypeError as te:
                return f"BeamStructureSolutionRun signature mismatch: {sig} ({te})"

    try:
        # 1) userID만 필수로 받기(클라가 파일 안 보낼 수도 있음)
        user_id = extract_user_id(request)
        if not user_id or not USERID_RE.match(user_id):
            return jsonify({"error": "Invalid or missing userID"}), 400

        members = mongo.db.members
        data = members.find_one({'userID': user_id})
        userName = data.get('userName')
        userCompany = data.get('userCompany')
        userDept = data.get('userDept')

        Beam.BeamStructureSolutionRun(user_id, userName, userCompany, userDept)

        # 2) ──[★ 폴더 생성 규칙: 원래대로 ★]─────────────────────
        #    기존 유틸을 그대로 사용 (request를 넘기는 기존 패턴 유지)
        userFolder = UserFolderCreate(userDirectory, request)
        folder_name_only = os.path.basename(userFolder)

        # (선택) 추적용 메타
        try:
            with open(os.path.join(userFolder, "meta.txt"), "w", encoding="utf-8") as f:
                f.write(f"userID: {user_id}\n")
        except Exception:
            pass  # 메타 실패해도 흐름 계속

        # 3) 파일이 왔다면 저장 (첫 번째 .bdf만 사용). 안 왔으면 해석 없이 JSON만 반환 가능
        files = request.files.getlist('file')
        bdf_path = None
        if files:
            filename = secure_filename(files[0].filename)
            if not filename.lower().endswith(".bdf"):
                return jsonify({"error": f"Only .bdf files are allowed: {filename}"}), 400
            bdf_path = os.path.join(userFolder, filename)
            files[0].save(bdf_path)

        # 4) Nastran 실행 (파일이 있는 경우에만). 공백/한글 경로 안전하게 리스트 인자 + cwd 지정
        f06_filename = None
        stdout_tail = ""
        stderr_tail = ""
        retcode = None

        if bdf_path:
            result = subprocess.run(
                ["nastran", bdf_path],
                cwd=userFolder,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            retcode = result.returncode
            stdout_tail = result.stdout[-1000:] if result.stdout else ""
            stderr_tail = result.stderr[-1000:] if result.stderr else ""

            # 확실한 f06 이름 계산 (대소문자 안전)
            base = os.path.splitext(os.path.basename(bdf_path))[0]
            f06_filename = base + ".f06"
            f06_path = os.path.join(userFolder, f06_filename)

            if not os.path.exists(f06_path):
                # f06이 없으면 디버깅 정보를 JSON으로 반환 (클라가 JSON을 기대)
                return jsonify({
                    "error": "f06 result file not found.",
                    "retcode": retcode,
                    "stdout_tail": stdout_tail,
                    "stderr_tail": stderr_tail,
                    "userFolder": folder_name_only
                }), 500

        # 5) BeamStructureSolutionRun 호출(선택): 폴더/ID만 넘김
        beam_run_status = "skipped"
        beam_run_result = None
        try:
            beam_run_result = run_beam_solution(userFolder, user_id)
            if beam_run_result is None or isinstance(beam_run_result, (str, int, float)):
                beam_run_status = "ok"
            else:
                beam_run_status = "ok"
        except Exception as e:
            beam_run_status = "failed"
            beam_run_result = str(e)

        # 6) 업로드 응답은 **항상 JSON** (클라 수정 불필요)
        return jsonify({
            "message": "OK",
            "userID": user_id,
            "userFolder": folder_name_only,   # ← 클라가 이 값 사용
            "f06_filename": f06_filename,     # ← 클라가 이 값 사용(파일 안 온 경우 None)
            "beamRun": beam_run_status,
            "beamResult": (str(beam_run_result)[:800] if beam_run_result is not None else None),
            "retcode": retcode,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




####################################################################################################################
@blueprint.route('/csvToBdf/download/<folder>/<filename>', methods=['GET'])
def download_csvToBdf(folder, filename):
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\CsvToBdf")
    try:
        target_folder = os.path.join(userDirectory, folder)

        # 경로 검증
        if not os.path.exists(os.path.join(target_folder, filename)):
            return jsonify({"error": f"{filename} not found in {folder}"}), 404

        return send_from_directory(directory=target_folder, path=filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint.route('/moduleUnit', methods=['GET', 'POST'])
def ModuleUnit():
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\ModuleUnit")

    # programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\HiTessBeam\CsvToBdf")

    # 인포겟 프로그램에서 출력된 bdf 파일에서 해석에 필요한 요소들을 추출해내는 메써드
    def InforgetMode(inforgetBDF):
        ModulePoint_idx_list = []
        lifting_method = None
        with open(inforgetBDF, 'r', encoding='utf8') as f:
            lines = f.readlines()
            for line_idx in range(len(lines)):
                if '$$Hydro' in lines[line_idx] or '$$Goliat' in lines[line_idx]:
                    if '$$Hydro' in lines[line_idx]:
                        lifting_method = 0
                    elif '$$Goliat' in lines[line_idx]:
                        lifting_method = 1
                    ModulePoint_info_idx_start = line_idx + 1
                    ModulePoint_idx_list.append(ModulePoint_info_idx_start)

                if '$$------------------------------------------------------------------------------$' in lines[
                    line_idx]:
                    ModulePoint_info_idx_end = line_idx
                    ModulePoint_idx_list.append(ModulePoint_info_idx_end)
                    break

        ModuleInfo_text = lines[ModulePoint_idx_list[0]: ModulePoint_idx_list[1]]

        ModuleInfo_dict = {}
        lineLength_list = []
        for line in ModuleInfo_text:
            clean_item = line.replace('$$', '').strip()
            parts = clean_item.split()
            category = int(parts[0].split('-')[0])  # '1-1'에서 '1' 추출
            data_value = (int(parts[1]), int(parts[2]))  # 두 번째와 세 번째 인덱스 값 (정수 변환)

            # 카테고리에 따라 그룹화하여 첫 번째 인덱스 값만 저장
            if category not in ModuleInfo_dict:
                ModuleInfo_dict[category] = [data_value[0]]
                lineLength_list.append(data_value[1])
            else:
                ModuleInfo_dict[category].append(data_value[0])

        ModuleInfo_list = list(ModuleInfo_dict.values())

        return inforgetBDF, ModuleInfo_list, lineLength_list, lifting_method

    try:
        # 1. 사용자 폴더 생성
        userFolder = UserFolderCreate(userDirectory, request)

        file = request.files['file']
        filename = secure_filename(file.filename)
        if not filename.endswith('.bdf'):
            return jsonify({"error": "Only .bdf files are allowed"}), 400


        input_bdf = os.path.join(userFolder, filename)
        output_bdf = input_bdf.replace(".bdf", "_r.bdf")
        output_bdf = os.path.join(userFolder, output_bdf)
        file.save(input_bdf)

        members = mongo.db.members

        user_id = request.form.get("userID")
        programName = request.form.get("programName")

        data = members.find_one({'userID': user_id})
        userName = data.get('userName')
        userCompany = data.get('userCompany')
        userDept = data.get('userDept')

        HiTESS_Beam.ModuleGroupUnitRun(programName, user_id, userName, userCompany, userDept)

        bdf, HookTrolley_list, lineLength, lifting_method = InforgetMode(input_bdf)
        HookTrolleyInstance = HookTrolley(bdf, output_bdf, HookTrolley_list, lineLength, Safety_Factor=1.2,
                                          lifting_method=lifting_method,
                                          analysis=True, debugPrint=True)  # trolley 모델
        HookTrolleyInstance.HookTrolleyRun()

        folder_name_only = os.path.basename(userFolder)
        bdf_filename = os.path.basename(output_bdf)
        f06_filename = bdf_filename.replace(".bdf", ".f06")
        txt_filename = bdf_filename.replace(".bdf", ".txt")

        return jsonify({
            "message": "서버에서 BDF 변환이 완료되었습니다.",
            "userFolder": folder_name_only,
            "bdf_filename": bdf_filename,
            "f06_filename": f06_filename,
            "txt_filename": txt_filename
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint.route('/moduleUnit/download/<folder>/<filename>', methods=['GET'])
def download_moduleUnit(folder, filename):
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\ModuleUnit")
    try:
        target_folder = os.path.join(userDirectory, folder)

        # 경로 검증
        if not os.path.exists(os.path.join(target_folder, filename)):
            return jsonify({"error": f"{filename} not found in {folder}"}), 404

        return send_from_directory(directory=target_folder, path=filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 승하선 사다리 해석 라우터
@blueprint.route('/LadderAnalysis', methods=['GET', 'POST'])
def LadderAnalysis():
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\LadderAnalysis")
    LadderPython = r"C:\Users\HHI\KHM\HiTessCloud_Flask\main\PythonModule\Infoget_ladder_R3.py"
    try:
        # 1. 사용자 폴더 생성
        userFolder = UserFolderCreate(userDirectory, request)

        file = request.files['file']
        filename = secure_filename(file.filename)
        if not filename.endswith('.bdf'):
            return jsonify({"error": "Only .bdf files are allowed"}), 400

        members = mongo.db.members

        user_id = request.form.get("userID")
        data = members.find_one({'userID': user_id})
        userName = data.get('userName')
        userCompany = data.get('userCompany')
        userDept = data.get('userDept')

        HiTESS_Beam.LadderRun(user_id, userName, userCompany, userDept)

        Ladder_bdf = os.path.join(userFolder, filename)
        file.save(Ladder_bdf)
        arg = r"python " + LadderPython + f" {Ladder_bdf}"
        subprocess.Popen(arg).wait()

        folder_name_only = os.path.basename(userFolder)
        report_name = filename.replace(".bdf", ".xlsx")

        return jsonify({
            "message": "서버에서 BDF 수신이 완료되었습니다.",
            "userFolder": folder_name_only,
            "report_name" : report_name
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint.route('/LadderAnalysis/download/<folder>/<filename>', methods=['GET'])
def download_LadderAnalysis(folder, filename):
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\LadderAnalysis")
    try:
        target_folder = os.path.join(userDirectory, folder)
        print('target_folder 확인 : ', target_folder)

        # 경로 검증
        if not os.path.exists(os.path.join(target_folder, filename)):
            return jsonify({"error": f"{filename} not found in {folder}"}), 404

        return send_from_directory(directory=target_folder, path=filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint.route('/BdfToCsv', methods=['GET', 'POST'])
def TempSupportExtract():
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\TempSupportExtract")
    # programDirectory = os.path.join(baseDirectory, r"main\EngineeringPrograms\HiTessBeam\CsvToBdf")

    try:
        # 1. 사용자 폴더 생성
        userFolder = UserFolderCreate(userDirectory, request)

        file = request.files['file']
        filename = secure_filename(file.filename)
        if not filename.endswith('.bdf'):
            return jsonify({"error": "Only .bdf files are allowed"}), 400

        input_bdf = os.path.join(userFolder, filename)
        file.save(input_bdf)

        csvFile = BdfToCsv(input_bdf)

        folder_name_only = os.path.basename(userFolder)
        csv_filename = os.path.basename(csvFile)

        return jsonify({
            "message": "서버에서 csv 변환이 완료되었습니다.",
            "userFolder": folder_name_only,
            "csv_filename": csv_filename,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint.route('/BdfToCsv/download/<folder>/<filename>', methods=['GET'])
def download_bdfToCsv(folder, filename):
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\TempSupportExtract")
    try:
        target_folder = os.path.join(userDirectory, folder)

        # 경로 검증
        if not os.path.exists(os.path.join(target_folder, filename)):
            return jsonify({"error": f"{filename} not found in {folder}"}), 404

        return send_from_directory(directory=target_folder, path=filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# 파일 다운로드 라우트 (클라가 별도 GET으로 호출)
@blueprint.route('/beamStructureAnalysis/download/<userFolder>/<fname>', methods=['GET'])
def BeamStructureAnalysisDownload(userFolder, fname):
    from flask import send_file, abort
    # ──[원래 베이스 경로 유지]──────────────────────────────────
    userDirectory = os.path.join(baseDirectory, r"main\userConnection\HiTessBeam\BeamStructureAnalysis")

    fpath = os.path.join(userDirectory, userFolder, fname)
    if not os.path.exists(fpath):
        return abort(404)
    return send_file(fpath, as_attachment=True, mimetype="text/plain", download_name=fname)


