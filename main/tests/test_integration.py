"""클라이언트-서버 통합 테스트"""
import pytest
import time
import random
import string
from services.api_service import GameAPIClient
from core.session_manager import SessionManager


@pytest.fixture
def api_client():
    """API 클라이언트 fixture"""
    client = GameAPIClient(base_url="http://localhost:8000")
    yield client
    # 테스트 후 세션 정리
    client.session_manager.clear_session_file()
    client.shutdown()


@pytest.fixture
def random_username():
    """랜덤 사용자명 생성"""
    return f"test_user_{''.join(random.choices(string.ascii_lowercase, k=8))}"


class TestServerConnection:
    """서버 연결 테스트"""

    def test_server_health_check(self, api_client):
        """서버 헬스 체크"""
        result = api_client.check_connection()
        assert result is True, "서버에 연결할 수 없습니다"

    def test_server_health_check_async(self, api_client):
        """비동기 서버 헬스 체크"""
        future = api_client.check_connection_async()
        result = future.result(timeout=5)
        assert result is True, "비동기 서버 연결 실패"


class TestAuthenticationFlow:
    """인증 플로우 통합 테스트"""

    def test_register_login_flow(self, api_client, random_username):
        """회원가입 -> 로그인 플로우"""
        password = "test1234"

        # 1. 회원가입
        success, data, error = api_client.register(random_username, password)
        assert success is True, f"회원가입 실패: {error}"
        assert data is not None
        assert "user" in data
        assert data["user"]["username"] == random_username

        # 2. 로그아웃
        api_client.logout()
        assert not api_client.is_logged_in()

        # 3. 로그인
        success, data, error = api_client.login(random_username, password)
        assert success is True, f"로그인 실패: {error}"
        assert data is not None
        assert "access_token" in data
        assert api_client.is_logged_in()

    def test_duplicate_registration(self, api_client, random_username):
        """중복 회원가입 테스트"""
        password = "test1234"

        # 첫 번째 회원가입
        success1, _, _ = api_client.register(random_username, password)
        assert success1 is True

        # 동일한 아이디로 재가입 시도
        success2, _, error2 = api_client.register(random_username, password)
        assert success2 is False, "중복 회원가입이 차단되어야 합니다"
        assert error2 is not None

    def test_invalid_login(self, api_client):
        """잘못된 로그인 정보 테스트"""
        success, _, error = api_client.login("nonexistent_user", "wrongpassword")
        assert success is False, "존재하지 않는 사용자로 로그인되면 안 됩니다"
        assert error is not None


class TestScoreManagement:
    """점수 관리 통합 테스트"""

    @pytest.fixture(autouse=True)
    def setup_logged_in_user(self, api_client, random_username):
        """로그인된 사용자 설정"""
        password = "test1234"
        api_client.register(random_username, password)
        api_client.login(random_username, password)
        yield
        api_client.logout()

    def test_save_score(self, api_client):
        """점수 저장 테스트"""
        score = 100

        success, data, error = api_client.save_score(score)
        assert success is True, f"점수 저장 실패: {error}"
        assert data is not None
        assert data["score"] == score

    def test_save_multiple_scores(self, api_client):
        """여러 점수 저장 테스트"""
        scores = [50, 100, 75, 200, 150]

        for score in scores:
            success, _, error = api_client.save_score(score)
            assert success is True, f"점수 {score} 저장 실패: {error}"

        # 내 점수 조회
        success, my_scores, error = api_client.get_my_scores()
        assert success is True, f"점수 조회 실패: {error}"
        assert len(my_scores) >= len(scores)

    def test_get_my_stats(self, api_client):
        """내 통계 조회 테스트"""
        # 점수 몇 개 저장
        scores = [100, 200, 150]
        for score in scores:
            api_client.save_score(score)

        # 통계 조회
        success, stats, error = api_client.get_my_stats()
        assert success is True, f"통계 조회 실패: {error}"
        assert stats is not None
        assert "total_games" in stats
        assert stats["total_games"] >= len(scores)
        assert "highest_score" in stats
        assert stats["highest_score"] == max(scores)

    def test_get_top_scores(self, api_client):
        """상위 점수 조회 테스트"""
        success, scores, error = api_client.get_top_scores(limit=10)
        assert success is True, f"상위 점수 조회 실패: {error}"
        assert isinstance(scores, list)
        # 점수가 내림차순으로 정렬되어 있는지 확인
        if len(scores) > 1:
            for i in range(len(scores) - 1):
                assert scores[i]["score"] >= scores[i + 1]["score"]


class TestAsyncAPIOperations:
    """비동기 API 작업 테스트"""

    def test_async_register(self, api_client, random_username):
        """비동기 회원가입 테스트"""
        password = "test1234"

        future = api_client.register_async(random_username, password)
        success, data, error = future.result(timeout=10)

        assert success is True, f"비동기 회원가입 실패: {error}"
        assert data is not None

    def test_async_login(self, api_client, random_username):
        """비동기 로그인 테스트"""
        password = "test1234"

        # 먼저 회원가입
        api_client.register(random_username, password)
        api_client.logout()

        # 비동기 로그인
        future = api_client.login_async(random_username, password)
        success, data, error = future.result(timeout=10)

        assert success is True, f"비동기 로그인 실패: {error}"
        assert api_client.is_logged_in()

    def test_multiple_async_operations(self, api_client, random_username):
        """여러 비동기 작업 동시 실행 테스트"""
        password = "test1234"

        # 회원가입 및 로그인
        api_client.register(random_username, password)
        api_client.login(random_username, password)

        # 여러 점수를 비동기로 저장
        futures = []
        scores = [100, 200, 150, 300, 250]

        for score in scores:
            future = api_client.save_score_async(score)
            futures.append(future)

        # 모든 Future 완료 대기
        for future in futures:
            success, _, error = future.result(timeout=10)
            assert success is True, f"비동기 점수 저장 실패: {error}"


class TestSessionPersistence:
    """세션 지속성 테스트"""

    def test_session_persistence(self, random_username):
        """세션 저장 및 로드 테스트"""
        password = "test1234"

        # 첫 번째 클라이언트로 로그인
        client1 = GameAPIClient()
        client1.register(random_username, password)
        client1.login(random_username, password)
        assert client1.is_logged_in()
        client1.shutdown()

        # 두 번째 클라이언트 생성 (세션 자동 로드)
        client2 = GameAPIClient()
        assert client2.is_logged_in(), "세션이 저장되고 로드되어야 합니다"
        assert client2.session_manager.username == random_username

        # 정리
        client2.session_manager.clear_session_file()
        client2.shutdown()


class TestErrorHandling:
    """오류 처리 테스트"""

    def test_save_score_without_login(self, api_client):
        """로그인 없이 점수 저장 시도"""
        success, _, error = api_client.save_score(100)
        assert success is False
        assert "로그인" in error

    def test_invalid_server_url(self):
        """잘못된 서버 URL 테스트"""
        client = GameAPIClient(base_url="http://invalid-server:9999")
        success, _, error = client.register("test", "test1234")
        assert success is False
        assert "네트워크 오류" in error or "오류" in error
        client.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
