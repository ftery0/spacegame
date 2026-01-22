"""서비스 레이어 테스트"""
import pytest
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from services.score_service import ScoreService
from models.user import User
from core.security import verify_password


class TestAuthService:
    """인증 서비스 테스트"""

    def test_register_user_success(self, db: Session):
        """사용자 등록 성공"""
        service = AuthService(db)
        success, user, error = service.register_user("newuser", "password123")

        assert success is True
        assert user is not None
        assert user.username == "newuser"
        assert verify_password("password123", user.hashed_password)
        assert error is None

    def test_register_duplicate_user(self, db: Session, test_user: User):
        """중복 사용자 등록"""
        service = AuthService(db)
        success, user, error = service.register_user("testuser", "password123")

        assert success is False
        assert user is None
        assert "이미 사용 중인" in error

    def test_login_user_success(self, db: Session, test_user: User):
        """사용자 로그인 성공"""
        service = AuthService(db)
        success, user, error = service.login_user("testuser", "testpass123")

        assert success is True
        assert user is not None
        assert user.username == "testuser"
        assert error is None

    def test_login_invalid_username(self, db: Session):
        """존재하지 않는 사용자명으로 로그인"""
        service = AuthService(db)
        success, user, error = service.login_user("nonexistent", "password123")

        assert success is False
        assert user is None
        assert "사용자 이름 또는 비밀번호" in error

    def test_login_invalid_password(self, db: Session, test_user: User):
        """잘못된 비밀번호로 로그인"""
        service = AuthService(db)
        success, user, error = service.login_user("testuser", "wrongpassword")

        assert success is False
        assert user is None
        assert "사용자 이름 또는 비밀번호" in error

    def test_create_access_token(self, db: Session, test_user: User):
        """액세스 토큰 생성"""
        service = AuthService(db)
        token = service.create_access_token_for_user(test_user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_access_token(self, db: Session, test_user: User):
        """액세스 토큰 검증"""
        service = AuthService(db)
        token = service.create_access_token_for_user(test_user)
        success, username, error = service.verify_access_token(token)

        assert success is True
        assert username == "testuser"
        assert error is None

    def test_verify_invalid_token(self, db: Session):
        """잘못된 토큰 검증"""
        service = AuthService(db)
        success, username, error = service.verify_access_token("invalid_token")

        assert success is False
        assert username is None
        assert "토큰이 유효하지 않습니다" in error

    def test_get_user_by_username(self, db: Session, test_user: User):
        """사용자명으로 사용자 조회"""
        service = AuthService(db)
        user = service.get_user_by_username("testuser")

        assert user is not None
        assert user.username == "testuser"

    def test_get_nonexistent_user(self, db: Session):
        """존재하지 않는 사용자 조회"""
        service = AuthService(db)
        user = service.get_user_by_username("nonexistent")

        assert user is None


class TestScoreService:
    """점수 서비스 테스트"""

    def test_create_score(self, db: Session, test_user: User):
        """점수 생성"""
        service = ScoreService(db)
        score_data = service.create_score(test_user.id, 150)

        assert score_data is not None
        assert score_data["score"] == 150
        assert score_data["user_id"] == test_user.id
        assert score_data["username"] == "testuser"

    def test_get_user_scores(self, db: Session, test_user: User):
        """사용자 점수 조회"""
        service = ScoreService(db)
        # 여러 점수 저장
        service.create_score(test_user.id, 100)
        service.create_score(test_user.id, 200)
        service.create_score(test_user.id, 150)

        scores = service.get_user_scores(test_user.id)

        assert len(scores) == 3
        assert all(s["user_id"] == test_user.id for s in scores)

    def test_get_top_scores(self, db: Session, multiple_users: list, multiple_scores: list):
        """상위 점수 조회"""
        service = ScoreService(db)
        top_scores = service.get_top_scores(limit=10)

        assert len(top_scores) > 0
        # 내림차순 확인
        for i in range(len(top_scores) - 1):
            assert top_scores[i]["score"] >= top_scores[i + 1]["score"]

    def test_get_recent_scores(self, db: Session, test_user: User):
        """최근 점수 조회"""
        service = ScoreService(db)
        service.create_score(test_user.id, 100)
        service.create_score(test_user.id, 200)

        recent = service.get_recent_scores(limit=10)

        assert len(recent) >= 2

    def test_get_user_statistics(self, db: Session, test_user: User):
        """사용자 통계 조회"""
        service = ScoreService(db)
        service.create_score(test_user.id, 100)
        service.create_score(test_user.id, 200)
        service.create_score(test_user.id, 150)

        stats = service.get_user_statistics(test_user.id)

        assert stats is not None
        assert stats["total_games"] == 3
        assert stats["best_score"] == 200
        assert stats["average_score"] == pytest.approx(150.0)
        assert stats["rank"] >= 1

    def test_get_statistics_no_scores(self, db: Session, test_user: User):
        """점수가 없을 때 통계 조회"""
        service = ScoreService(db)
        stats = service.get_user_statistics(test_user.id)

        assert stats is None

    def test_delete_score_success(self, db: Session, test_user: User):
        """점수 삭제 성공"""
        service = ScoreService(db)
        score_data = service.create_score(test_user.id, 100)
        score_id = score_data["id"]

        success = service.delete_score(test_user.id, score_id)

        assert success is True

        # 삭제 확인
        scores = service.get_user_scores(test_user.id)
        assert len(scores) == 0

    def test_delete_nonexistent_score(self, db: Session, test_user: User):
        """존재하지 않는 점수 삭제"""
        service = ScoreService(db)
        success = service.delete_score(test_user.id, 99999)

        assert success is False

    def test_delete_other_user_score(self, db: Session, multiple_users: list):
        """다른 사용자의 점수 삭제 시도"""
        service = ScoreService(db)
        user1, user2 = multiple_users[0], multiple_users[1]

        # user1의 점수 저장
        score_data = service.create_score(user1.id, 100)
        score_id = score_data["id"]

        # user2가 user1의 점수 삭제 시도
        success = service.delete_score(user2.id, score_id)

        assert success is False

    def test_user_ranking(self, db: Session, multiple_users: list):
        """사용자 랭킹 계산"""
        service = ScoreService(db)
        users = multiple_users

        # 각 사용자에게 다른 점수 할당
        service.create_score(users[0].id, 500)
        service.create_score(users[1].id, 400)
        service.create_score(users[2].id, 300)
        service.create_score(users[3].id, 200)

        # 각 사용자의 통계 확인
        stats_500 = service.get_user_statistics(users[0].id)
        stats_400 = service.get_user_statistics(users[1].id)
        stats_300 = service.get_user_statistics(users[2].id)

        # 랭킹이 올바르게 계산되었는지 확인
        assert stats_500["rank"] == 1
        assert stats_400["rank"] == 2
        assert stats_300["rank"] == 3
