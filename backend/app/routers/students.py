from sqlalchemy.orm import Session                       # 加 Session
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.models.student import Student                   # 加 ORM 模型
from app.database import get_db                          # 加 get_db
from fastapi import APIRouter, HTTPException, Depends, Header
from app.auth import get_current_user_id                 # 加 get_current_user_id
# from datetime import datetime   # ← 这行删掉，不需要手动处理时间了

# 定义路由
router = APIRouter()

# ── 内存数据库（临时，Step 2 替换为 MySQL） ──
# students_db = []
# next_id = 1

def verify_token(authorization: str = Header(...)):
    """从 Authorization header 提取并验证 token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization 格式错误")
    token = authorization.split(" ")[1]
    return get_current_user_id(token)




@router.get("/students/")
def list_students(page: int = 1, size: int = 10,keyword: str = "" ,db: Session = Depends(get_db),user_id: int = Depends(verify_token)):
    """获取学生列表（含分页）"""
    query = db.query(Student)
    if keyword:
        query = query.filter(Student.name.contains(keyword))
    items = query.offset((page - 1) * size).limit(size).all()
    total = query.count()
    return {"items": [StudentResponse.model_validate(s) for s in items], "total": total}


@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int,db: Session = Depends(get_db),user_id: int = Depends(verify_token)):
    """获取单个学生详情"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student


@router.post("/students/", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate,db: Session = Depends(get_db),user_id: int = Depends(verify_token)):
    """新增学生"""
    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate,db: Session = Depends(get_db),user_id: int = Depends(verify_token)):
    """更新学生信息"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")

    for key, value in student.model_dump().items():
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/students/{student_id}")
def delete_student(student_id: int,db: Session = Depends(get_db),user_id: int = Depends(verify_token)):
    """删除学生"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")

    db.delete(db_student)
    db.commit()
    return {"message": "删除成功"}
