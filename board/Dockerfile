FROM python:3.10-slim

WORKDIR /works

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# FastAPI 실행
CMD ["python", "main.py"]
