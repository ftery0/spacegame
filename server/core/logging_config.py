"""로깅 설정"""
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """
    로깅 설정

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
            logging.FileHandler(log_dir / "server.log", encoding="utf-8"),
        ]
    )

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # passlib과 bcrypt 관련 로그도 출력
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("bcrypt").setLevel(logging.WARNING)

    return logging.getLogger(__name__)
