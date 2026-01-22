"""Test configuration and fixtures"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from main import app
from database import Base, get_db
from models.user import User
from models.score import Score
from core.security import get_password_hash

# 테스트 데이터베이스 설정
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """테스트용 데이터베이스 세션 오버라이드"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """테스트용 데이터베이스"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """테스트 클라이언트"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """테스트용 사용자 생성"""
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(client: TestClient, db: Session) -> str:
    """테스트용 사용자 토큰 생성"""
    # 먼저 사용자 생성
    response = client.post(
        "/api/auth/register",
        json={"username": "tokenuser", "password": "tokenpass123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def test_score(db: Session, test_user: User) -> Score:
    """테스트용 점수 생성"""
    score = Score(user_id=test_user.id, score=100)
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@pytest.fixture
def multiple_users(db: Session) -> list:
    """여러 테스트용 사용자 생성"""
    users = []
    for i in range(5):
        user = User(
            username=f"user{i}",
            hashed_password=get_password_hash(f"pass{i}")
        )
        db.add(user)
        users.append(user)
    db.commit()

    for user in users:
        db.refresh(user)

    return users


@pytest.fixture
def multiple_scores(db: Session, multiple_users: list) -> list:
    """여러 테스트용 점수 생성"""
    scores = []
    score_values = [100, 200, 150, 300, 250]

    for user, score_value in zip(multiple_users, score_values):
        score = Score(user_id=user.id, score=score_value)
        db.add(score)
        scores.append(score)

    db.commit()

    for score in scores:
        db.refresh(score)

    return scores
