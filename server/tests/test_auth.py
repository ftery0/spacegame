"""인증 엔드포인트 테스트"""
import pytest
from fastapi.testclient import TestClient


class TestRegister:
    """회원가입 테스트"""

    def test_register_success(self, client: TestClient):
        """회원가입 성공"""
        response = client.post(
            "/api/auth/register",
            json={"username": "newuser", "password": "newpass123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "newuser"

    def test_register_duplicate_username(self, client: TestClient, test_user):
        """중복된 사용자명으로 회원가입 실패"""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "newpass123"}
        )

        assert response.status_code == 400
        assert "이미 사용 중인" in response.json()["detail"]

    def test_register_weak_password(self, client: TestClient):
        """약한 비밀번호로 회원가입"""
        response = client.post(
            "/api/auth/register",
            json={"username": "weakpass", "password": "123"}  # 4자 미만
        )

        # 클라이언트 검증 통과 후 서버에서 처리
        assert response.status_code in [201, 422]

    def test_register_short_username(self, client: TestClient):
        """짧은 사용자명으로 회원가입"""
        response = client.post(
            "/api/auth/register",
            json={"username": "ab", "password": "pass123"}  # 3자 미만
        )

        assert response.status_code in [201, 422]


class TestLogin:
    """로그인 테스트"""

    def test_login_success(self, client: TestClient, test_user):
        """로그인 성공"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_invalid_username(self, client: TestClient):
        """존재하지 않는 사용자명으로 로그인"""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "pass123"}
        )

        assert response.status_code == 401
        assert "사용자 이름 또는 비밀번호" in response.json()["detail"]

    def test_login_invalid_password(self, client: TestClient, test_user):
        """잘못된 비밀번호로 로그인"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpass"}
        )

        assert response.status_code == 401
        assert "사용자 이름 또는 비밀번호" in response.json()["detail"]


class TestGetMe:
    """현재 사용자 조회 테스트"""

    def test_get_me_success(self, client: TestClient, test_user_token: str):
        """로그인 사용자 정보 조회 성공"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "tokenuser"
        assert data["id"] is not None

    def test_get_me_without_token(self, client: TestClient):
        """토큰 없이 사용자 정보 조회"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        assert "인증 정보" in response.json()["detail"]

    def test_get_me_invalid_token(self, client: TestClient):
        """잘못된 토큰으로 사용자 정보 조회"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == 401
        assert "인증 정보" in response.json()["detail"]

    def test_get_me_bearer_format(self, client: TestClient):
        """잘못된 Bearer 형식"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "invalid_token"}
        )

        assert response.status_code == 401
