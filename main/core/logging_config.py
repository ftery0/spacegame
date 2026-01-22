"""클라이언트 로깅 설정"""
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """
    클라이언트 로깅 설정

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 로그 포맷 설정
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 루트 로거 설정
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 콘솔 핸들러
            logging.StreamHandler(sys.stdout),
            # 파일 핸들러
            logging.FileHandler(log_dir / "client.log", encoding="utf-8"),
        ]
    )

    # Pygame 로그 레벨 조정 (pygame은 기본적으로 로깅을 많이 하지 않음)
    logging.getLogger("pygame").setLevel(logging.WARNING)

    return logging.getLogger(__name__)
