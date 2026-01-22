"""Session manager for application state management"""
import json
import os
from typing import Optional
from pathlib import Path
from cryptography.fernet import Fernet
import base64


class SessionManager:
    """싱글톤 패턴으로 구현된 세션 관리자"""

    _instance = None
    _session_file = "session.json"
    _key_file = ".session_key"

    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """세션 관리자 초기화"""
        if self._initialized:
            return

        self._initialized = True
        self.username: Optional[str] = None
        self.user_id: Optional[int] = None
        self.access_token: Optional[str] = None
        self.token_type: str = "bearer"
        self._cipher = self._get_cipher()

        self._load_session()

    def _get_cipher(self) -> Fernet:
        """
        암호화 키 가져오기 또는 생성

        Returns:
            Fernet: 암호화/복호화 객체
        """
        key_path = Path(self._key_file)

        if key_path.exists():
            # 기존 키 로드
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            # 새 키 생성
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)

        return Fernet(key)

    def _encrypt_token(self, token: str) -> str:
        """
        토큰 암호화

        Args:
            token: 평문 토큰

        Returns:
            str: 암호화된 토큰 (base64 인코딩)
        """
        if not token:
            return ""
        encrypted = self._cipher.encrypt(token.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_token(self, encrypted_token: str) -> str:
        """
        토큰 복호화

        Args:
            encrypted_token: 암호화된 토큰

        Returns:
            str: 복호화된 토큰
        """
        if not encrypted_token:
            return ""
        try:
            encrypted = base64.b64decode(encrypted_token.encode())
            decrypted = self._cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception:
            # 복호화 실패 시 빈 문자열 반환
            return ""

    def _load_session(self):
        """저장된 세션 로드 (암호화된 토큰 복호화)"""
        try:
            if os.path.exists(self._session_file):
                with open(self._session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.username = data.get("username")
                    self.user_id = data.get("user_id")
                    # 암호화된 토큰 복호화
                    encrypted_token = data.get("access_token")
                    self.access_token = self._decrypt_token(encrypted_token) if encrypted_token else None
                    self.token_type = data.get("token_type", "bearer")
        except (json.JSONDecodeError, IOError):
            # 세션 파일이 손상된 경우 무시
            pass

    def _save_session(self):
        """현재 세션 저장 (토큰 암호화)"""
        try:
            # 토큰 암호화
            encrypted_token = self._encrypt_token(self.access_token) if self.access_token else None

            data = {
                "username": self.username,
                "user_id": self.user_id,
                "access_token": encrypted_token,
                "token_type": self.token_type
            }
            with open(self._session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError:
            # 파일 저장 실패 시 무시
            pass

    def login(self, username: str, user_id: int, access_token: str, token_type: str = "bearer"):
        """
        사용자 로그인 처리

        Args:
            username: 사용자명
            user_id: 사용자 ID
            access_token: JWT 액세스 토큰
            token_type: 토큰 타입 (기본값: "bearer")
        """
        self.username = username
        self.user_id = user_id
        self.access_token = access_token
        self.token_type = token_type
        self._save_session()

    def logout(self):
        """사용자 로그아웃 처리"""
        self.username = None
        self.user_id = None
        self.access_token = None
        self.token_type = "bearer"
        self._save_session()

    def is_logged_in(self) -> bool:
        """
        로그인 여부 확인

        Returns:
            bool: 로그인 상태 여부
        """
        return self.access_token is not None and self.username is not None

    def get_auth_header(self) -> Optional[dict]:
        """
        API 요청용 인증 헤더 생성

        Returns:
            Optional[dict]: {"Authorization": "Bearer <token>"} 또는 None
        """
        if not self.is_logged_in():
            return None

        return {
            "Authorization": f"{self.token_type} {self.access_token}"
        }

    def get_token(self) -> Optional[str]:
        """
        액세스 토큰 반환

        Returns:
            Optional[str]: 액세스 토큰 또는 None
        """
        return self.access_token

    def clear_session_file(self):
        """세션 파일 삭제"""
        try:
            if os.path.exists(self._session_file):
                os.remove(self._session_file)
        except IOError:
            pass

    def __repr__(self):
        """세션 정보 문자열 표현"""
        return f"<SessionManager username={self.username} logged_in={self.is_logged_in()}>"
