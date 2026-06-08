# Day 2：连接 MySQL 数据库 — SQLAlchemy + ORM

> 全栈学生管理系统 ｜ 学习日期：2026-06-02

---

## 目录

- [一、Step 2 概述](#一step-2-概述)
- [二、database.py — 数据库连接配置](#二databasepy--数据库连接配置)
- [三、ORM 模型 — models/student.py](#三orm-模型--modelsstudentpy)
- [四、路由改造 — 从内存到数据库](#四路由改造--从内存到数据库)
- [五、main.py 改造 — 启动时自动建表](#五mainpy-改造--启动时自动建表)
- [六、完整知识点归纳](#六完整知识点归纳)
- [七、项目结构（当前状态）](#七项目结构当前状态)
- [八、面试题](#八面试题)
- [九、下一步预告](#九下一步预告)

---

## 一、Step 2 概述

### 做了什么

把 Step 1 中内存列表（`students_db`）存储替换为 MySQL 数据库，通过 SQLAlchemy ORM 操作数据库。

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/database.py` | **新建** | 数据库连接配置、会话工厂、依赖函数 |
| `app/models/__init__.py` | **新建** | models 包标记 |
| `app/models/student.py` | **新建** | ORM 模型，描述 students 表结构 |
| `app/main.py` | **修改** | 加 lifespan 启动时自动建表 |
| `app/routers/students.py` | **修改** | 列表操作 → 数据库查询 |

---

## 二、database.py — 数据库连接配置

### 代码

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "mysql+pymysql://root:root123@localhost:3308/student_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 逐行解释

| 代码 | 作用 |
|------|------|
| `DATABASE_URL` | 数据库连接字符串，格式：`驱动://用户名:密码@主机:端口/库名` |
| `create_engine()` | 创建数据库引擎，底层管理连接池 |
| `sessionmaker()` | 会话工厂，每次调用 `SessionLocal()` 获得一个新会话 |
| `class Base` | ORM 模型基类，所有模型继承它，SQLAlchemy 才能识别 |
| `get_db()` | FastAPI 依赖函数，请求进来时获取会话，结束时自动关闭 |

### 关键概念：三层架构

```
FastAPI 路由 → SessionLocal（会话） → engine（引擎） → MySQL
```

- **Engine（引擎）**：跟 MySQL 保持长期连接，管理连接池
- **Session（会话）**：每次请求创建一个，用完关闭。事务的边界
- **get_db()**：FastAPI 的 `Depends` 机制自动管理会话生命周期

---

## 三、ORM 模型 — models/student.py

### 代码

```python
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
```

### 映射关系

| ORM 写法 | 对应 SQL |
|---------|---------|
| `class Student(Base)` | 定义一张表 |
| `__tablename__ = "students"` | 表名 |
| `Column(Integer, primary_key=True)` | `id INT PRIMARY KEY` |
| `Column(String(50), nullable=False)` | `name VARCHAR(50) NOT NULL` |
| `Column(Enum("男", "女", "其他"))` | `gender ENUM('男','女','其他')` |
| `Column(DateTime, server_default=func.now())` | `created_at DATETIME DEFAULT CURRENT_TIMESTAMP` |

### 关键概念：什么是 ORM

**ORM（Object-Relational Mapping，对象关系映射）** — 用 Python 类描述数据库表，操作对象就是操作数据。

```
Python 对象           SQL 语句              数据库
───────────────────────────────────────────────
Student(name="张三")    →  INSERT INTO ...    → 写入一行
db.query(Student)      →  SELECT *           → 读取数据
db_student.name = "李四" →  UPDATE ... SET   → 修改数据
db.delete(db_student)  →  DELETE FROM        → 删除数据
```

**好处**：不用写 SQL，用 Python 语法操作数据库。SQLAlchemy 自动翻译。

**`server_default` 与 `default` 的区别**：

| | server_default | default |
|---|---|---|
| 谁填充 | MySQL 数据库 | Python/SQLAlchemy |
| 什么时候生效 | INSERT 时由 MySQL 填充 | ORM 创建对象时填充 |
| 推荐用哪个 | 推荐（跟数据库结构一致） | 不推荐（跟表定义不一致） |

### 为什么要有 `models/` 目录

不是必须的，但为了代码组织。所有模型文件放在 `models/` 下，跟 `routers/`、`schemas/` 平级，文件多了不混乱。

---

## 四、路由改造 — 从内存到数据库

### 改了什么

```python
# 新增的导入
from fastapi import Depends                # 依赖注入
from sqlalchemy.orm import Session         # ORM 会话类型
from app.models.student import Student     # ORM 模型
from app.database import get_db            # 获取数据库会话

# 删掉的内容
students_db = []    # 不再需要内存列表
next_id = 1         # 不再需要手动自增（数据库自动生成）
```

### 5 个接口的 CRUD 对照

| 操作 | 原来（内存列表） | 现在（数据库） |
|------|-----------------|---------------|
| 列表 | `students_db[start:end]` | `db.query(Student).offset().limit().all()` |
| 查询 | `for s in students_db: if s["id"] == id` | `db.query(Student).filter(Student.id == id).first()` |
| 新增 | 手动组装 dict + append | `db.add()` → `db.commit()` → `db.refresh()` |
| 更新 | 遍历 → 替换数据 | 查出 → 改属性 → `db.commit()` |
| 删除 | `students_db.pop(index)` | `db.delete()` → `db.commit()` |

### 代码对比（POST 新增）

**原来：**
```python
global next_id
new_student = student.model_dump()
new_student["id"] = next_id
next_id += 1
new_student["created_at"] = datetime.now()
new_student["updated_at"] = datetime.now()
students_db.append(new_student)
return new_student
```

**现在：**
```python
db_student = Student(**student.model_dump())
db.add(db_student)
db.commit()
db.refresh(db_student)
return db_student
```

**`**student.model_dump()`** — 把 Pydantic 模型转成字典，再展开成关键字参数传给 `Student()`。等价于：

```python
data = student.model_dump()
db_student = Student(name=data["name"], age=data["age"], gender=data["gender"], ...)
```

### 每个数据库操作的作用

| 操作 | 作用 | 类比 |
|------|------|------|
| `db.add(obj)` | 把对象加入会话，准备 INSERT | 写草稿 |
| `db.commit()` | 提交事务，真正写入数据库 | 点"保存" |
| `db.refresh(obj)` | 从数据库重新读取（拿到自增 ID、默认时间） | 刷新页面 |
| `db.query(Model)` | 开始一次查询 | 打开查询窗口 |
| `db.delete(obj)` | 标记删除该行 | 放入回收站 |

**为什么需要 `commit()` 才能写入？** 这叫"事务"——如果你先新增一个学生、再更新他的信息，两步可以一起 `commit()`，失败了可以全部回滚，不会出现写一半的情况。

### 更新操作的写法

```python
for key, value in student.model_dump().items():
    setattr(db_student, key, value)
```

`setattr(obj, 属性名, 值)` 等价于 `obj.属性名 = 值`。这行循环把前端传过来的所有字段逐个赋值到 ORM 对象上，不需要每个字段手写一遍。

---

## 五、main.py 改造 — 启动时自动建表

### 代码

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import students
from app.models import student                 # 必须导入，否则 create_all 不知道建什么表


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)      # 启动时检查并创建所有表
    yield
    # 关闭时无需操作


app = FastAPI(title="学生管理系统", version="1.0", lifespan=lifespan)
app.include_router(students.router, prefix="/api/v1")
```

### lifespan 机制

- `yield` **之前** → 启动时执行（建表、加载配置、连接池预热）
- `yield` **之后** → 关闭时执行（关闭连接、清理资源）
- 这是 FastAPI 新版生命周期写法，替代旧版 `@app.on_event("startup")`

### `from app.models import student` 的作用

这行看似没用（没调用任何函数），但实际上它导入了 `student.py` 文件，Python 执行时会把 `Student` 类注册到 `Base.metadata` 上。`create_all()` 遍历 `metadata` 才知道要建哪些表。没有这行，`create_all()` 不会建 `students` 表。

---

## 六、完整知识点归纳

### SQLAlchemy

| 概念 | 一句话解释 |
|------|-----------|
| **Engine** | 数据库引擎，管理连接池，跟 MySQL 保持长连接 |
| **Session** | 数据库会话，每次请求一个，用完关闭。事务的边界 |
| **ORM 模型** | 用 Python 类描述表结构，`Column()` 定义列 |
| **`query()`** | 查询入口，后面接 `.filter()`、`.offset()`、`.limit()` |
| **`commit()`** | 提交事务，不 commit 不写入数据库 |
| **`refresh()`** | 从数据库重新读取，拿到自动生成的值（ID、时间戳） |

### ORM 核心

- 每个 Python 类 = 一张表，每个属性 = 一列
- 操作对象 = 操作数据，SQLAlchemy 自动翻译成 SQL
- 不必手动写 SQL，但要知道 ORM 背后生成的是什么

### FastAPI Depends

- `Depends(get_db)` 让 FastAPI 自动管理数据库会话
- 请求进来 → 调用 `get_db()` → 拿到 `db` → 注入路由函数
- 请求结束 → 自动执行 `finally` 块 → `db.close()`
- 不需要在每个路由里手动 `SessionLocal()` 和 `db.close()`

### 包（Package）机制

- 目录下有 `__init__.py` 才能被 `from app.models import xxx` 导入
- `models/` 目录跟 `routers/`、`schemas/` 平级，各管各的事

---

## 七、项目结构（当前状态）

```
项目一/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # 入口 + lifespan 自动建表
│   │   ├── database.py            # ★ 新增：数据库连接配置
│   │   ├── models/                # ★ 新增：ORM 模型包
│   │   │   ├── __init__.py
│   │   │   └── student.py         # ★ 新增：Student ORM 模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── student.py         # Pydantic 校验模型
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── students.py        # ★ 修改：列表→数据库操作
│   ├── venv/
│   └── requirements.txt
├── docs/
│   ├── day-1-notes.md
│   └── day-2-notes.md             # ★ 本文件
├── .vscode/
├── .gitignore
└── project-1-learning-plan.md
```

---

## 八、面试题

**Q：ORM 和直接写 SQL 比有什么优缺点？**
A：优点是不用写 SQL、跨数据库切换方便、防止 SQL 注入。缺点是复杂查询学习成本高、性能不如手写 SQL。

**Q：SQLAlchemy 的 Session 是线程安全的吗？**
A：不是。所以 FastAPI 每次请求通过 `Depends(get_db)` 创建新会话，而不是共用一个。

**Q：`db.commit()` 不调用会怎样？**
A：数据不会写入数据库。会话关闭时自动回滚，相当于操作没发生。

**Q：`refresh()` 是必须的吗？**
A：不是必须的，但如果不调用，返回的对象里自增 ID 是 `None`，时间戳是 Python 生成的值而不是数据库的值。

---

## 九、Day 2 练习题 + 答案

### 选择题

| # | 题目 | 答案 | 解析 |
|---|------|------|------|
| 1 | `3308` 是什么端口？ | **B** 宿主机映射端口 | `-p 3308:3306`，左侧宿主机，右侧容器 |
| 2 | `create_engine()` 返回值？ | **B** 数据库引擎（管理连接池） | |
| 3 | `SessionLocal()` 返回？ | **B** 新的数据库会话 | |
| 4 | `get_db()` 用 `yield` 而非 `return`？ | **B** Depends 需要生成器管理生命周期 | `finally` 保证会话关闭 |
| 5 | `db.commit()` 不调用会怎样？ | **B** 数据不写入，关闭时自动回滚 | |
| 6 | `db.refresh(obj)` 作用？ | **B** 从数据库重读对象，拿到自增 ID 和时间戳 | |
| 7 | `Column(Enum("男","女","其他"))` 对应 SQL？ | **B** `gender ENUM('男','女','其他')` | |
| 8 | `server_default` vs `default`？ | **B** `server_default` 由 MySQL 填充，`default` 由 Python 填充 | |
| 9 | 哪个不对应 SQL 写入？ | **B** `db.query()` | query 只读，不写 |
| 10 | lifespan 中 `yield` 前后？ | **A** 之前启动，之后关闭 | |
| 11 | `from app.models import student` 必须写？ | **B** 把 Student 类注册到 Base.metadata，create_all 才能建表 | |
| 12 | `**student.model_dump()` 中 `**` 作用？ | **B** 把字典展开成关键字参数 | |
| 13 | 哪个不是三层架构？ | **C** Router（路由） | 三层是 Engine → Session → MySQL |
| 14 | `db.query().filter().first()` 返回？ | **B** 第一个匹配对象，没有则 None | |
| 15 | Session 线程安全？ | **B** 不是，所以每次请求创建新 Session | |

### 填空题答案

**2.1 database.py**
```python
sessionmaker
mysql+pymysql://root:root123@localhost:3308/student_db
create_engine
engine
SessionLocal
close
```

**2.2 ORM 模型**
```python
Enum
Student
students
False
True
func.now()
```
> 注意最后一个空是 `func.now()`，`func` 是 SQLAlchemy 的 SQL 函数模块，`now()` 是 MySQL 的 `NOW()` 函数。

**2.3 CRUD 对照**
```
列表：db.query(Student).offset().limit().all()
查询：db.query(Student).filter(Student.id == id).first()
新增：db.add() → db.commit() → db.refresh()
更新：setattr() → db.commit()
删除：db.delete() → db.commit()
```

### 改错题答案

**3.1 database.py**
1. 缺少 `DeclarativeBase` 导入和 `Base` 类定义 — 所有 ORM 模型需要继承 `Base`
2. `get_db()` 用 `return` 而非 `yield` — 使用 `yield` + `try/finally` 才能确保会话关闭

**3.2 ORM 模型**
1. 类名 `student` 应为 `Student`（Python 类名大写驼峰）
2. `__tablename__ = "student"` 应为 `"students"`（与表名一致）
3. `id` 列缺少 `autoincrement=True`

**3.3 新增接口**
1. 缺少 `response_model=StudentResponse`
2. `Student(student.model_dump())` 应为 `Student(**student.model_dump())` — 缺少 `**` 展开
3. 缺少 `db.refresh(db_student)` — 否则返回的对象没有自增 ID 和时间戳

### 代码补全答案

**4.1 更新接口**
```python
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    for key, value in student.model_dump().items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student
```

**4.2 删除接口**
```python
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(db_student)
    db.commit()
    return {"message": "删除成功"}
```

### 简答题答案

**5.1 事务：** 事务是一组数据库操作，要么全部成功（commit），要么全部回滚（rollback）。防止写一半时出错导致数据不一致。比如更新学生表和班级表，第二步失败时第一步也撤销。

**5.2 三层架构：**
- **Engine（引擎）**：跟 MySQL 保持长连接，管理连接池
- **Session（会话）**：每次请求创建，用完关闭，事务的边界
- **MySQL（数据库）**：实际存储数据

**5.3 `setattr(obj, key, value)`：** 等价于 `obj.key = value` 的动态版本。用来遍历 `model_dump()` 的键值对批量赋值，不必每字段手写一句。

---

## 十、下一步预告

**Step 3：Vue3 前端页面**。写一个带表格、表单、弹窗的网页，通过 Axios 调用后端 5 个接口，实现真正的全栈增删改查。
