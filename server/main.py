"""FastAPI 게임 서버 메인 애플리케이션"""
import logging
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import traceback

from database import init_db
from core.config import settings
from core.logging_config import setup_logging
from routers import auth, scores, game_stats, achievements, difficulties

# 로깅 설정
setup_logging(log_level=getattr(settings, "LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Rate Limiting 설정
limiter = Limiter(key_func=get_remote_address)

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="회원가입, 로그인, 점수 저장 및 랭킹 시스템을 제공하는 API",
    version=settings.APP_VERSION
)

# 전역 예외 처리 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """모든 예외를 로깅하고 사용자에게 안전한 메시지 반환"""
    logger.error(
        f"예외 발생 - 경로: {request.url.path}, 메서드: {request.method}\n"
        f"에러: {str(exc)}\n"
        f"상세:\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}
    )

# Rate Limiting 미들웨어 추가
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요."
))

# CORS 설정 (제한적인 도메인만 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(scores.router)
app.include_router(game_stats.router)
app.include_router(achievements.router)
app.include_router(difficulties.router)


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터베이스 초기화"""
    init_db()
    logger.info("✅ 데이터베이스 초기화 완료")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "원석 부수기 게임 서버",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
