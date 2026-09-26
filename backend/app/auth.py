from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException

# ── 配置 ──
SECRET_KEY = "student-management-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ── 密码哈希 ──
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """密码 -> 哈希（bcrypt 自动加盐）"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配存储的哈希"""
    return pwd_context.verify(plain_password, hashed_password)

# ── JWT ──
def create_access_token(data: dict) -> str:
    """生成 JWT token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id(token: str) -> int:
    """验证 token 并返回用户 ID（失败抛 401）"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise JWTError("token 中缺少 sub")
        user_id = int(sub)
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")
