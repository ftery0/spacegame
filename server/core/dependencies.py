"""의존성 주입 설정"""
from functools import lru_cache
from .config import Settings


@lru_cache()
def get_settings() -> Settings:
    """
    애플리케이션 설정 싱글톤 제공

    Returns:
        Settings: 애플리케이션 설정
    """
    return Settings()
