from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from app.database import Base


class Student(Base):
    """学生 ORM 模型 — 对应数据库 students 表"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum("男", "女", "其他"), nullable=False, default="其他")
    grade = Column(String(20), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
