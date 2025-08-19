"""공통 인증 및 인가 로직"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
# from passlib.context import CryptContext
import structlog

from ..config.settings import settings
from .exceptions import AuthenticationError, AuthorizationError

logger = structlog.get_logger(__name__)
security = HTTPBearer(auto_error=False)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthManager:
    """인증 관리자"""
    
    def __init__(self):
        self.secret_key = settings.security.secret_key
        self.algorithm = settings.security.algorithm
        self.access_token_expire_minutes = settings.security.access_token_expire_minutes
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info("Access token created", subject=data.get("sub"), expires=expire)
            return encoded_jwt
        except Exception as e:
            logger.error("Failed to create access token", error=str(e))
            raise AuthenticationError("토큰 생성 실패")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 만료 시간 확인 (jwt.decode가 자동으로 확인하지만 명시적으로)
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise AuthenticationError("토큰이 만료되었습니다")
            
            logger.debug("Token verified successfully", subject=payload.get("sub"))
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise AuthenticationError("토큰이 만료되었습니다")
        except jwt.JWTError as e:
            logger.warning("Invalid token", error=str(e))
            raise AuthenticationError("유효하지 않은 토큰입니다")
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        # return pwd_context.hash(password)
        raise NotImplementedError("비밀번호 해시화는 구현되지 않았습니다")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        # return pwd_context.verify(plain_password, hashed_password)
        raise NotImplementedError("비밀번호 검증은 구현되지 않았습니다")


# 전역 인증 관리자 인스턴스
auth_manager = AuthManager()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """현재 사용자 정보 추출"""
    
    if not credentials:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = auth_manager.verify_token(credentials.credentials)
        return payload
    except AuthenticationError as e:
        logger.warning("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """선택적 사용자 정보 추출 (인증 선택사항)"""
    
    if not credentials:
        return None
    
    try:
        return auth_manager.verify_token(credentials.credentials)
    except AuthenticationError:
        return None


def require_permission(permission: str):
    """특정 권한 요구 데코레이터"""
    
    def permission_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = user.get("permissions", [])
        
        if permission not in user_permissions:
            logger.warning(
                "Permission denied",
                user_id=user.get("sub"),
                required_permission=permission,
                user_permissions=user_permissions
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"권한이 부족합니다: {permission}"
            )
        
        return user
    
    return permission_checker


def require_role(role: str):
    """특정 역할 요구 데코레이터"""
    
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        user_roles = user.get("roles", [])
        
        if role not in user_roles:
            logger.warning(
                "Role check failed",
                user_id=user.get("sub"),
                required_role=role,
                user_roles=user_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"필요한 역할이 없습니다: {role}"
            )
        
        return user
    
    return role_checker


class APIKeyValidator:
    """API 키 검증자"""
    
    def __init__(self, valid_keys: Optional[Dict[str, str]] = None):
        self.valid_keys = valid_keys or {}
    
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> str:
        """API 키 검증"""
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API 키가 필요합니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        api_key = credentials.credentials
        
        # API 키 검증 로직 (실제 환경에서는 데이터베이스 조회)
        if api_key not in self.valid_keys:
            logger.warning("Invalid API key", api_key_prefix=api_key[:8] + "...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 API 키입니다"
            )
        
        logger.info("API key validated", service=self.valid_keys[api_key])
        return api_key


# 서비스별 API 키 검증자 (예시)
confluence_api_key = APIKeyValidator({
    "conf_dev_key_123": "confluence_dev",
    "conf_prod_key_456": "confluence_prod"
})

jira_api_key = APIKeyValidator({
    "jira_dev_key_123": "jira_dev",
    "jira_prod_key_456": "jira_prod"
})

slack_api_key = APIKeyValidator({
    "slack_dev_key_123": "slack_dev",
    "slack_prod_key_456": "slack_prod"
})