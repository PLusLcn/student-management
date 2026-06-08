from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentCreate(BaseModel):
    """新增学生时前端要传的数据"""
    name: str
    age: int
    gender: Optional[str] = "其他"
    grade: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class StudentUpdate(BaseModel):
    """更新学生时前端要传的数据（和创建一样，全量更新）"""
    name: str
    age: int
    gender: Optional[str] = "其他"
    grade: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class StudentResponse(BaseModel):
    """返回给前端的学生数据格式"""
    id: int
    name: str
    age: int
    gender: Optional[str] = "其他"
    grade: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
