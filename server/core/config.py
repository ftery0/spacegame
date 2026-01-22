"""애플리케이션 설정 관리"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    APP_NAME: str = "원석 부수기 게임 서버"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./game.db"

    # 보안
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # 요청 개수
    RATE_LIMIT_PERIOD: int = 60  # 시간(초)

    class Config:
        """설정 클래스"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 싱글톤 설정 인스턴스
settings = Settings()
