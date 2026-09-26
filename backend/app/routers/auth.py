from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()

# ── 请求/响应模型 ──
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ── 注册 ──
@router.post("/register", status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """注册新用户"""
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    db_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "注册成功", "user_id": db_user.id}

# ── 登录 ──
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """登录，返回 JWT token"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
