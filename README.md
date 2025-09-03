# OhgoodpayML
Ohgoodpay Reco&amp;Analytics

## 개발 환경(venv) 빠른 시작

### 1) Python 버전 확인
```bash
python --version
# 또는 Windows에서
py -3.11 --version
```
### 2) 가상환경 설정
- 가상환경 이름은 꼭 .venv가 아니어도 됨
```
python -m venv .venv 
.\.venv\Scripts\Activate

# windows / git bash
python -m venv .venv
source .venv/Scripts/activate

# macOS / Linux / WSL
python -m venv .venv
source .venv/bin/activate
```

### 3) 패키지 설치
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4) 서버 실행
```
uvicorn app.main:app --reload --port 8000

# 비활성화
deactivate 
```
- Swagger: http://localhost:8000/docs
- 데모 페이지: http://localhost:8000/v1/demo
- 핑: http://localhost:8000/v1/ping
