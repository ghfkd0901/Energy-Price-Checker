import pandas as pd

# 원본 파일 경로
file_path = "/mnt/data/지역별_표준기화율.csv"

# CSV 파일 불러오기
df = pd.read_csv(file_path, encoding="utf-8-sig")  # 원래 인코딩 유지

# 컬럼명 확인 후 변경
print("변경 전 컬럼명:", df.columns.tolist())

# 컬럼명을 "지역", "표준기화율"로 변경
df.columns = ["지역", "표준기화율"]

# 변경된 컬럼 확인
print("변경 후 컬럼명:", df.columns.tolist())

# 새로운 CSV 파일 경로
new_file_path = "/mnt/data/지역별_표준기화율_수정.csv"

# UTF-8로 저장
df.to_csv(new_file_path, index=False, encoding="utf-8")

print(f"✅ 파일 저장 완료: {new_file_path}")