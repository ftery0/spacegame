"""점수 엔드포인트 테스트"""
import pytest
from fastapi.testclient import TestClient


class TestCreateScore:
    """점수 저장 테스트"""

    def test_create_score_success(self, client: TestClient, test_user_token: str):
        """점수 저장 성공"""
        response = client.post(
            "/api/scores",
            json={"score": 150},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 150
        assert data["user_id"] is not None
        assert data["username"] == "tokenuser"

    def test_create_score_without_auth(self, client: TestClient):
        """인증 없이 점수 저장"""
        response = client.post(
            "/api/scores",
            json={"score": 150}
        )

        assert response.status_code == 401

    def test_create_score_zero(self, client: TestClient, test_user_token: str):
        """0점 저장"""
        response = client.post(
            "/api/scores",
            json={"score": 0},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 201
        assert response.json()["score"] == 0

    def test_create_score_high(self, client: TestClient, test_user_token: str):
        """높은 점수 저장"""
        response = client.post(
            "/api/scores",
            json={"score": 999999},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 201
        assert response.json()["score"] == 999999


class TestGetTopScores:
    """상위 점수 조회 테스트"""

    def test_get_top_scores(self, client: TestClient, multiple_scores):
        """상위 점수 조회"""
        response = client.get("/api/scores/top?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # 점수가 내림차순인지 확인
        for i in range(len(data) - 1):
            assert data[i]["score"] >= data[i + 1]["score"]

    def test_get_top_scores_limit(self, client: TestClient, multiple_scores):
        """제한된 상위 점수 조회"""
        response = client.get("/api/scores/top?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_top_scores_max_limit(self, client: TestClient, multiple_scores):
        """최대 제한보다 큰 값으로 조회"""
        response = client.get("/api/scores/top?limit=500")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 100

    def test_get_top_scores_empty(self, client: TestClient, db):
        """데이터가 없을 때 상위 점수 조회"""
        response = client.get("/api/scores/top")

        assert response.status_code == 200
        assert response.json() == []


class TestGetRecentScores:
    """최근 점수 조회 테스트"""

    def test_get_recent_scores(self, client: TestClient, multiple_scores):
        """최근 점수 조회"""
        response = client.get("/api/scores/recent?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_recent_scores_default_limit(self, client: TestClient, multiple_scores):
        """기본 제한으로 최근 점수 조회"""
        response = client.get("/api/scores/recent")

        assert response.status_code == 200
        assert len(response.json()) <= 20


class TestGetMyScores:
    """내 점수 조회 테스트"""

    def test_get_my_scores_success(self, client: TestClient, test_user_token: str, db):
        """내 점수 조회 성공"""
        # 점수 저장
        client.post(
            "/api/scores",
            json={"score": 100},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        # 조회
        response = client.get(
            "/api/scores/my",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["score"] == 100

    def test_get_my_scores_without_auth(self, client: TestClient):
        """인증 없이 내 점수 조회"""
        response = client.get("/api/scores/my")

        assert response.status_code == 401

    def test_get_my_scores_empty(self, client: TestClient, test_user_token: str):
        """점수가 없을 때 내 점수 조회"""
        response = client.get(
            "/api/scores/my",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 200
        assert response.json() == []


class TestGetMyStats:
    """내 통계 조회 테스트"""

    def test_get_my_stats_success(self, client: TestClient, test_user_token: str):
        """내 통계 조회 성공"""
        # 점수 저장
        scores = [100, 200, 150]
        for score in scores:
            client.post(
                "/api/scores",
                json={"score": score},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )

        # 통계 조회
        response = client.get(
            "/api/scores/stats",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_games"] == 3
        assert data["best_score"] == 200
        assert data["average_score"] == pytest.approx(150.0)
        assert data["rank"] >= 1
        assert data["username"] == "tokenuser"

    def test_get_my_stats_without_auth(self, client: TestClient):
        """인증 없이 내 통계 조회"""
        response = client.get("/api/scores/stats")

        assert response.status_code == 401

    def test_get_my_stats_no_plays(self, client: TestClient, test_user_token: str):
        """플레이 기록이 없을 때 통계 조회"""
        response = client.get(
            "/api/scores/stats",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 404
        assert "플레이 기록" in response.json()["detail"]


class TestDeleteScore:
    """점수 삭제 테스트"""

    def test_delete_score_success(self, client: TestClient, test_user_token: str):
        """점수 삭제 성공"""
        # 점수 저장
        score_response = client.post(
            "/api/scores",
            json={"score": 100},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        score_id = score_response.json()["id"]

        # 삭제
        delete_response = client.delete(
            f"/api/scores/{score_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert delete_response.status_code == 204

        # 삭제 확인
        my_scores = client.get(
            "/api/scores/my",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert len(my_scores.json()) == 0

    def test_delete_nonexistent_score(self, client: TestClient, test_user_token: str):
        """존재하지 않는 점수 삭제"""
        response = client.delete(
            "/api/scores/99999",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        assert response.status_code == 403

    def test_delete_other_user_score(self, client: TestClient, db):
        """다른 사용자의 점수 삭제 시도"""
        # 첫 번째 사용자 생성 및 점수 저장
        user1_response = client.post(
            "/api/auth/register",
            json={"username": "user1", "password": "pass1"}
        )
        user1_token = user1_response.json()["access_token"]
        score_response = client.post(
            "/api/scores",
            json={"score": 100},
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        score_id = score_response.json()["id"]

        # 두 번째 사용자 생성
        user2_response = client.post(
            "/api/auth/register",
            json={"username": "user2", "password": "pass2"}
        )
        user2_token = user2_response.json()["access_token"]

        # 다른 사용자의 점수 삭제 시도
        delete_response = client.delete(
            f"/api/scores/{score_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )

        assert delete_response.status_code == 403
