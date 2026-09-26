from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import student, user
from app.routers.students import router as students_router
from app.routers.auth import router as auth_router
from app.routers.export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="学生管理系统", version="1.0", lifespan=lifespan)


# CORS 中间件：允许前端 localhost:5173 访问
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(students_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(export_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "学生管理系统 API 运行中"}

