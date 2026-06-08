# Day 1：环境搭建 + FastAPI CRUD 入门

> 全栈学生管理系统 ｜ 学习日期：2026-06-02

---

## 目录

- [一、Step 0a：环境准备](#一step-0a环境准备)
- [二、Step 0b：项目设计](#二step-0b项目设计)
- [三、Step 0b 续：venv 与 pip](#三step-0b-续venv-与-pip)
- [四、Step 1：FastAPI CRUD](#四step-1fastapi-crud)
- [五、完整知识点归纳](#五完整知识点归纳)
- [六、最终项目结构](#六最终项目结构)

---

## 一、Step 0a：环境准备

### 做了什么

安装 VSCode 插件、配置 Git、Docker 启动 MySQL。

### 关键命令

| 命令 | 解释 |
|------|------|
| `git config --global user.name "名字"` | 设置 Git 全局用户名 |
| `git config --global user.email "邮箱"` | 设置 Git 全局邮箱 |
| `git init` | 在当前目录创建 Git 仓库 |
| `git config --list` | 查看所有 Git 配置 |
| `docker run --name student-mysql -e MYSQL_ROOT_PASSWORD=root123 -e MYSQL_DATABASE=student_db -p 3308:3306 -d mysql:8.0` | 启动 MySQL 容器 |
| `docker ps` | 查看运行中的容器 |
| `docker rm student-mysql` | 删除指定容器 |

### Docker 参数含义

| 参数 | 含义 |
|------|------|
| `--name student-mysql` | 给容器命名，后续用这个名字管理容器 |
| `-e MYSQL_ROOT_PASSWORD=root123` | 设置 MySQL root 密码 |
| `-e MYSQL_DATABASE=student_db` | 自动创建指定数据库 |
| `-p 3308:3306` | 宿主机 3308 端口 → 容器内 3306 端口 |
| `-d` | 后台运行（detached） |
| `mysql:8.0` | 使用 MySQL 8.0 镜像 |

---

## 二、Step 0b：项目设计

### 目录结构

```
项目一/
├── backend/                # 后端代码
│   └── app/               # 应用主包
│       ├── __init__.py    # 包标记
│       ├── main.py        # 入口：创建 FastAPI 实例，挂载路由
│       ├── routers/       # 路由（控制器）
│       │   ├── __init__.py
│       │   └── students.py
│       └── schemas/       # 数据模型（请求/响应格式）
│           ├── __init__.py
│           └── student.py
├── docs/                   # 文档
├── .gitignore
└── requirements.txt
```

**`__init__.py` 作用**：让 Python 把目录当作"包"，这样才能用 `from app.routers import students` 这样的导入语法。

### 数据库设计

**表名**：`students`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | 主键、自增 | 唯一标识 |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| age | INT | NOT NULL | 年龄 |
| gender | ENUM('男','女','其他') | DEFAULT '其他' | 限制可取值 |
| grade | VARCHAR(20) | NOT NULL | 班级 |
| phone | VARCHAR(20) | 可选 | 用 VARCHAR 而非 INT，避免前导0丢失 |
| email | VARCHAR(100) | 可选 | |
| address | VARCHAR(200) | 可选 | |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### API 接口设计

| 方法 | 路径 | 功能 | 状态码 |
|------|------|------|--------|
| GET | `/api/v1/students/` | 列表（分页） | 200 |
| GET | `/api/v1/students/{id}` | 详情 | 200 / 404 |
| POST | `/api/v1/students/` | 新增 | 201 / 422 |
| PUT | `/api/v1/students/{id}` | 更新 | 200 / 404 |
| DELETE | `/api/v1/students/{id}` | 删除 | 200 / 404 |

统一格式：
- 成功 → JSON 数据
- 错误 → `{"detail": "错误描述"}`
- 接口前缀 `/api/v1`，方便后续版本升级

---

## 三、Step 0b 续：venv 与 pip

### 为什么需要虚拟环境

每个项目有自己的 Python 环境，不会相互影响。A 项目用 FastAPI 0.111，B 项目用 1.0，互不冲突。

### 关键命令

| 命令 | 解释 |
|------|------|
| `python -m venv backend/venv` | 在 backend 下创建虚拟环境 |
| `venv\Scripts\activate` | 激活虚拟环境（Windows CMD） |
| `. venv/Scripts/activate` | 激活虚拟环境（Windows Git Bash） |
| `pip install -r requirements.txt` | 批量安装依赖 |
| `pip install fastapi uvicorn` | 逐个安装包 |
| `venv\Scripts\python -c "import fastapi; print(fastapi.__version__)"` | 验证安装是否成功（CMD） |
| `. venv/Scripts/python -c "import fastapi; print(fastapi.__version__)"` | 验证安装是否成功（Git Bash） |

### requirements.txt

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pymysql==1.1.1
sqlalchemy==2.0.30
```

### 注意事项

- 激活后命令行出现 `(venv)` 前缀才是激活状态
- `pip install` 要在激活状态下执行，否则装到全局了
- Pylance 红波浪线 → `Ctrl+Shift+P` → Python: Select Interpreter → 选 venv 路径

---

## 四、Step 1：FastAPI CRUD

### main.py — 项目入口

```python
from fastapi import FastAPI
from app.routers import students

app = FastAPI(title="学生管理系统", version="1.0")

app.include_router(students.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "学生管理系统 API 运行中"}
```

- `FastAPI(title=..., version=...)` → 创建实例，标题显示在 Swagger 文档
- `include_router()` → 把路由模块挂到指定前缀
- `@app.get("/")` → 装饰器，声明 GET 方法 + 路径

### schemas/student.py — 数据模型

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StudentCreate(BaseModel):
    name: str
    age: int
    gender: Optional[str] = "其他"
    grade: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class StudentUpdate(BaseModel):
    """和 StudentCreate 相同（全量更新）"""
    name: str
    age: int
    gender: Optional[str] = "其他"
    grade: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class StudentResponse(BaseModel):
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
        from_attributes = True  # 支持从 ORM 对象转换
```

- Pydantic 做数据校验：类型不对、缺必填字段自动返回 422
- `Optional[str] = None` → 可选字段，不传就是 None
- `model_dump()` → 把 Pydantic 对象转成字典

### routers/students.py — 路由

```python
from fastapi import APIRouter, HTTPException
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from datetime import datetime

router = APIRouter()

students_db = []      # 临时内存数据库（Step 2 替换为 MySQL）
next_id = 1           # 自增 ID 种子
```

**5 个接口：**

```python
# ① 列表（分页）
@router.get("/students/", response_model=dict)
def list_students(page: int = 1, size: int = 10):
    start = (page - 1) * size
    end = start + size
    items = students_db[start:end]
    return {"items": items, "total": len(students_db)}

# ② 详情
@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail="学生不存在")

# ③ 新增
@router.post("/students/", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate):
    global next_id
    new_student = student.model_dump()
    new_student["id"] = next_id
    next_id += 1
    new_student["created_at"] = datetime.now()
    new_student["updated_at"] = datetime.now()
    students_db.append(new_student)
    return new_student

# ④ 更新
@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate):
    for index, existing in enumerate(students_db):
        if existing["id"] == student_id:
            updated = student.model_dump()
            updated["id"] = student_id
            updated["created_at"] = existing["created_at"]
            updated["updated_at"] = datetime.now()
            students_db[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="学生不存在")

# ⑤ 删除
@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    for index, existing in enumerate(students_db):
        if existing["id"] == student_id:
            students_db.pop(index)
            return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="学生不存在")
```

**知识点：**

- `APIRouter` → FastAPI 的路由模块化，每个文件写自己的一组接口
- `response_model` → 定义返回值格式，FastAPI 自动做数据过滤和文档生成
- `global next_id` → 函数内修改全局变量需要声明 global
- `HTTPException(status_code=404)` → 标准错误响应
- `enumerate()` → 同时拿到索引和元素，更新时方便

### 启动与测试

```bash
. venv/Scripts/activate
uvicorn app.main:app --reload --port 8000
```

- `--reload` → 代码变更自动重启
- 访问 `http://127.0.0.1:8000/docs` → Swagger 交互式文档
- 按顺序测试 5 个接口，全部通过

---

## 五、完整知识点归纳

### Git
- `git init` 创建仓库，`.gitignore` 排除无关文件
- `git config --global` 设置全局身份

### Docker
- 容器化运行数据库，环境隔离、启动/删除都干净
- 端口冲突换映射端口解决，容器名冲突 `docker rm` 解决

### Python 虚拟环境
- `venv` 为项目创建独立环境，依赖互不干扰
- 激活后才能操作当前环境的包
- VSCode 需要选择 venv 解释器才能消除 Pylance 报错

### FastAPI
- **入口**：`FastAPI()` 实例 + `uvicorn` 启动
- **路由**：`APIRouter` 模块化，`include_router` 挂载
- **数据模型**：Pydantic `BaseModel`，自动校验 + 文档
- **响应**：`response_model` 约束输出格式
- **错误**：`HTTPException` 统一返回 `{"detail": "..."}`
- **分页**：`page`/`size` 参数切片实现
- **Swagger**：`/docs` 自带交互文档，零配置

### RESTful API 设计惯例
- 统一前缀 `/api/v1`
- 资源名用复数 `/students/`
- POST 返回 201，其他成功返回 200
- 全量更新用 PUT

---

## 六、最终项目结构

```
项目一/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── students.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── student.py
│   ├── venv/
│   └── requirements.txt
├── docs/
│   └── day-1-notes.md         ← 本文件
├── .vscode/
│   └── settings.json
├── .gitignore
└── project-1-learning-plan.md
```

---

## 错误记录

| 错误 | 原因 | 解决 |
|------|------|------|
| Docker 3306 端口被占用 | 宿主机有其他程序占用 | `-p 3308:3306` 避开冲突 |
| Docker 容器名冲突 | 首次 run 失败但容器已创建 | `docker rm student-mysql` 后重试 |
| bash: ~touch: command not found | `~` 不能拼在命令前 | 去掉 `~` |
| Pylance 无法解析导入 fastapi | VSCode 没选 venv 解释器 | Select Interpreter → 选 venv 路径 |
| ModuleNotFoundError: No module named 'fastapi' | pip install 时没激活 venv | 激活后重新 pip install |

---

## 七、Day 1 练习题 + 答案

### 选择题

| # | 题目 | 答案 | 解析 |
|---|------|------|------|
| 1 | 创建 Git 仓库的命令？ | **B** `git init` | `git start` 不是 Git 命令 |
| 2 | `.gitignore` 的作用？ | **B** 声明不纳入版本控制的文件 | |
| 3 | `git config --global` 作用范围？ | **B** 所有 Git 项目 | `--global` 对当前用户全局生效 |
| 4 | `-p 3308:3306` 含义？ | **B** 宿主机 3308 → 容器 3306 | 左侧宿主机，右侧容器 |
| 5 | 后台运行参数？ | **B** `-d` | detached 模式 |
| 6 | 容器名冲突应执行？ | **C** `docker stop && docker rm` | 先停止再删除 |
| 7 | 虚拟环境作用？ | **B** 隔离不同项目的依赖版本 | |
| 8 | 激活后命令行前缀？ | **B** `(venv)` | |
| 9 | pip 成功但运行报 ModuleNotFoundError？ | **B** 没激活 venv | 包装到全局了 |
| 10 | `APIRouter` 作用？ | **B** 路由模块化拆分 | |
| 11 | 启动 FastAPI 的正确命令？ | **B** `uvicorn app.main:app --reload --port 8000` | |
| 12 | `--reload` 作用？ | **B** 代码变更自动重启 | 不是每次请求重载 |
| 13 | Swagger 默认地址？ | **B** `/docs` | |
| 14 | `Optional[str] = None` 含义？ | **B** 可选字段默认 None | |
| 15 | `from_attributes = True` 作用？ | **B** 支持从 ORM 对象转换 | |
| 16 | POST 创建成功状态码？ | **B** 201 | RESTful 规范 |

### 填空题答案

**2.1** `include_router`

**2.2** `str`、`int`、`None`

**2.3** `get`、`page`、`size`、`start`、`size`、`start`、`end`、`students_db`

**2.4** `students_db`、`pop`

### 改错题答案

**3.1 main.py**
1. `include_router` 缺少 `prefix="/api/v1"`
2. `return "字符串"` 应改为 `return {"message": "学生管理系统 API 运行中"}`

**3.2 新增接口**
1. 装饰器缺少 `status_code=201`
2. 函数内修改全局变量 `next_id` 需声明 `global next_id`

**3.3 详情接口**
1. 参数 `student_id: str` 类型错误，应为 `int`
2. 查不到时缺少 `raise HTTPException(status_code=404, detail="学生不存在")`

### 代码补全答案

**4.1 更新接口**
```python
if existing["id"] == student_id:
    updated = student.model_dump()
    students_db[index] = updated
    raise HTTPException(status_code=404, detail="学生不存在")
```

**4.2 Docker 启动**
```bash
docker run \
  --name student-mysql \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=student_db \
  -p 3308:3306 \
  -d \
  mysql:8.0
```

**4.3 分页计算**
```
page=3, size=10
start = (3-1) × 10 = 20
end = 20 + 10 = 30
students_db[20:30]，共 10 条（实际剩余 5 条），total = 25
```

### 简答题答案

**5.1 POST vs PUT：** PUT 是幂等的（同样数据更新多次结果相同），路径带 `{id}` 指定具体资源；POST 是非幂等的（每次创建新资源）。所以新增用 POST，更新用 PUT。

**5.2 `/api/v1/` 前缀：** 方便版本升级，后续 v2 放 `/api/v2/`，旧客户端不受影响。

**5.3 排查步骤：** ① 看命令行有无 `(venv)` 前缀 ② 没有则激活 venv ③ `pip list | grep fastapi` 检查是否已装 ④ 没装则 `pip install -r requirements.txt`

---

## 下一步

**Step 2**：用 SQLAlchemy 连接 MySQL，替换内存数据库为真实数据库。
