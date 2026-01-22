# 원석 부수기 게임 서버

FastAPI 기반 게임 점수 저장 및 랭킹 시스템 API 서버

## 기능

- ✅ 점수 저장
- ✅ 상위 랭킹 조회
- ✅ 최근 점수 조회
- ✅ 사용자별 통계 조회
- ✅ 자동 API 문서 (Swagger UI)

## 설치 방법

1. 가상환경 생성 및 활성화 (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

2. 패키지 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload
```

서버가 실행되면:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 1. 점수 저장
```http
POST /api/scores
Content-Type: application/json

{
  "username": "player1",
  "score": 150
}
```

### 2. 상위 랭킹 조회
```http
GET /api/scores/top?limit=10
```

### 3. 최근 점수 조회
```http
GET /api/scores/recent?limit=20
```

### 4. 사용자 통계 조회
```http
GET /api/scores/user/{username}
```

### 5. 점수 삭제 (관리자용)
```http
DELETE /api/scores/{score_id}
```

## 데이터베이스

- 개발 환경: SQLite (`spacegame.db`)
- 프로덕션: PostgreSQL (권장)

### 데이터베이스 스키마

**scores 테이블**
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer | 기본 키 |
| username | String(50) | 사용자 이름 |
| score | Integer | 점수 |
| created_at | DateTime | 생성 시간 |

## 배포

### Render.com 배포 (무료)

1. `render.yaml` 파일이 포함되어 있습니다
2. Render.com에서 "New Web Service" 선택
3. GitHub 저장소 연결
4. 자동으로 배포됩니다

### Railway 배포

```bash
railway login
railway init
railway up
```

## 개발

### 테스트 데이터 추가

```python
import requests

# 점수 저장
response = requests.post(
    "http://localhost:8000/api/scores",
    json={"username": "testuser", "score": 100}
)
print(response.json())
```

### 데이터베이스 초기화

```bash
# spacegame.db 파일을 삭제하면 서버 재시작 시 자동으로 재생성됩니다
rm spacegame.db
```

## 환경 변수

`.env` 파일을 생성하여 설정할 수 있습니다:

```bash
cp .env.example .env
```

## 기술 스택

- **FastAPI** - 웹 프레임워크
- **SQLAlchemy** - ORM
- **Pydantic** - 데이터 검증
- **Uvicorn** - ASGI 서버
- **SQLite/PostgreSQL** - 데이터베이스
