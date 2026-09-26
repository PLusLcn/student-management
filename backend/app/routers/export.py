from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.auth import get_current_user_id
from openpyxl import Workbook
from io import BytesIO
from fastapi import Header, HTTPException

router = APIRouter()

def verify_token(authorization: str = Header(...)):
    """从 Authorization header 提取并验证 token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization 格式错误")
    token = authorization.split(" ")[1]
    return get_current_user_id(token)
# 
@router.get("/students/export/excel")
def export_students_excel(
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    """导出学生列表为 Excel 文件"""
    students = db.query(Student).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "学生列表"

    # 表头
    headers = ["ID", "姓名", "年龄", "性别", "班级", "电话", "邮箱", "地址", "创建时间", "更新时间"]
    ws.append(headers)

    # 数据行
    for s in students:
        ws.append([s.id, s.name, s.age, s.gender, s.grade, s.phone, s.email, s.address,
                    s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "",
                    s.updated_at.strftime("%Y-%m-%d %H:%M:%S") if s.updated_at else ""])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=students.xlsx"}
    )
