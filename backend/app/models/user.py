from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class User(Base):
    """用户 ORM 模型 — 对应数据库 users 表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
