from pymongo import MongoClient
from datetime import datetime
import csv
import os

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")
db = client["HHI_member"]
analysis_collection = db["analysis"]
members_collection = db["members"]

# 사용자 정보 캐싱
member_info_dict = {}
for member in members_collection.find({}, {
    "_id": 0,
    "userID": 1,
    "userName": 1,
    "userDept": 1,
    "userCompany": 1,
    "userPos": 1
}):
    member_info_dict[member["userID"]] = {
        "userName": member.get("userName", ""),
        "userDept": member.get("userDept", ""),
        "userCompany": member.get("userCompany", ""),
        "userPos": member.get("userPos", "")
    }

# 로그 리스트 수집
rows = []
for record in analysis_collection.find({}, {
    "_id": 0, "userID": 1, "analysisType": 1, "analysisTime": 1
}):
    user_id = record.get("userID")
    analysis_type = record.get("analysisType")
    timestamp = record.get("analysisTime")

    # 시간 포맷 변환
    dt = datetime.fromtimestamp(timestamp / 1000)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')

    # 사용자 정보
    info = member_info_dict.get(user_id, {
        "userName": "Unknown",
        "userDept": "Unknown",
        "userCompany": "Unknown",
        "userPos": "Unknown"
    })

    rows.append([
        info["userName"],
        info["userCompany"],
        user_id,
        info["userDept"],
        analysis_type,
        formatted_time
    ])

# 시간 순 정렬
rows.sort(key=lambda x: x[-1])  # 접속시간 기준 정렬

# 저장 경로
output_path = os.path.join(r"C:\Users\HHI\KHM\Palantir\HiTESS_UserStastics", "HiTESS_log.csv")

# CSV 저장
with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["이름", "회사", "사번", "부서", "사용프로그램", "접속시간"])
    writer.writerows(rows)

print(f"[완료] 사용자 로그가 CSV로 저장되었습니다: {output_path}")
