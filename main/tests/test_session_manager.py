"""Session manager tests"""
import pytest
import os
from core.session_manager import SessionManager


@pytest.fixture
def session_manager():
    """SessionManager 픽스처"""
    # 싱글톤 초기화
    SessionManager._instance = None
    manager = SessionManager()
    yield manager
    # 테스트 후 정리
    if os.path.exists("session.json"):
        os.remove("session.json")


class TestSessionManager:
    """세션 관리자 테스트"""

    def test_singleton_pattern(self):
        """싱글톤 패턴 확인"""
        SessionManager._instance = None
        manager1 = SessionManager()
        manager2 = SessionManager()

        assert manager1 is manager2

    def test_login(self, session_manager):
        """로그인 처리"""
        session_manager.login(
            username="testuser",
            user_id=1,
            access_token="test_token_123",
            token_type="bearer"
        )

        assert session_manager.username == "testuser"
        assert session_manager.user_id == 1
        assert session_manager.access_token == "test_token_123"
        assert session_manager.is_logged_in() is True

    def test_logout(self, session_manager):
        """로그아웃 처리"""
        session_manager.login("testuser", 1, "token", "bearer")
        session_manager.logout()

        assert session_manager.username is None
        assert session_manager.user_id is None
        assert session_manager.access_token is None
        assert session_manager.is_logged_in() is False

    def test_is_logged_in(self, session_manager):
        """로그인 여부 확인"""
        assert session_manager.is_logged_in() is False

        session_manager.login("testuser", 1, "token", "bearer")
        assert session_manager.is_logged_in() is True

    def test_get_auth_header_logged_in(self, session_manager):
        """로그인 상태에서 인증 헤더 반환"""
        session_manager.login("testuser", 1, "token_123", "bearer")

        header = session_manager.get_auth_header()

        assert header is not None
        assert "Authorization" in header
        assert header["Authorization"] == "bearer token_123"

    def test_get_auth_header_not_logged_in(self, session_manager):
        """로그아웃 상태에서 인증 헤더 반환"""
        header = session_manager.get_auth_header()

        assert header is None

    def test_get_token(self, session_manager):
        """토큰 반환"""
        session_manager.login("testuser", 1, "token_456", "bearer")

        token = session_manager.get_token()

        assert token == "token_456"

    def test_get_token_not_logged_in(self, session_manager):
        """로그아웃 상태에서 토큰 반환"""
        token = session_manager.get_token()

        assert token is None

    def test_save_and_load_session(self):
        """세션 저장 및 로드"""
        SessionManager._instance = None

        # 로그인
        manager1 = SessionManager()
        manager1.login("testuser", 1, "token_789", "bearer")

        # 새 인스턴스 생성하면 저장된 세션을 로드해야 함
        SessionManager._instance = None
        manager2 = SessionManager()

        assert manager2.username == "testuser"
        assert manager2.user_id == 1
        assert manager2.access_token == "token_789"

        # 정리
        if os.path.exists("session.json"):
            os.remove("session.json")
