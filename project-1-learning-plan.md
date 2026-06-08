# 项目一：全栈学生管理系统 — 完整学习方案

> 基于《用Claude高效学习·行动大纲》扩展补充
> Python 3.13.4 / Node.js 24.15.0 / Git 2.54.0 / Docker 29.4.3

---

## 目录

- [一、总览流程图](#一总览流程图)
- [二、预备知识补充（15分钟速通）](#二预备知识补充15分钟速通)
- [三、Step 0a：准备阶段（0.5天）](#三step-0a准备阶段05天)
- [四、Step 0b：设计阶段（0.5天）](#四step-0b设计阶段05天)
- [五、Step 1：FastAPI 写 CRUD 接口（3-4天）](#五step-1fastapi-写-crud-接口3-4天)
- [六、Step 2：连接 MySQL 数据库（3-4天）](#六step-2连接-mysql-数据库3-4天)
- [七、Step 3：Vue3 写前端页面（3-5天）](#七step-3vue3-写前端页面3-5天)
- [八、Step 4：部署上线（2-3天）](#八step-4部署上线2-3天)
- [九、Step 5：加功能强化简历（选做，3-4天）](#九step-5加功能强化简历选做3-4天)
- [十、笔记模板](#十笔记模板)
- [十一、错误日志模板](#十一错误日志模板)
- [十二、前置知识自测表](#十二前置知识自测表)

---

## 一、总览流程图

```
┌─────────────────────────────────────────────────────────────┐
│              项目一：全栈学生管理系统                          │
│              Python + FastAPI + Vue3 + MySQL                  │
└─────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────┐
│  预备知识补充（15分钟速通）                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ if __name__、类型注解、try/except、async/await速览     │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                                │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Step 0a：准备阶段（0.5天）          Step 0b：设计阶段（0.5天）│
│  ┌─────────────────────────┐      ┌──────────────────────┐  │
│  │ 1. 知识检查（已完成）     │      │ 1. 项目目录结构       │  │
│  │ 2. 环境版本确认（已完成） │      │ 2. 数据库表设计       │  │
│  │ 3. VSCode插件安装        │      │ 3. API接口规范       │  │
│  │ 4. Git配置 + SSH         │      │ 4. 前端原型          │  │
│  └─────────────────────────┘      │ 5. 笔记模板定义       │  │
│                                    │ 6. 错误日志初始化     │  │
│                                    └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Step 1~5                                 │
│  Step 1: FastAPI 写 CRUD 接口（3-4天）                       │
│  Step 2: 连接 MySQL 数据库（3-4天）                           │
│  Step 3: Vue3 写前端页面（3-5天）                             │
│  Step 4: 部署上线（2-3天）                                    │
│  Step 5: 加功能强化简历（选做，3-4天）                         │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
            简历V1：全栈学生管理系统      GitHub 代码托管
            Docker 容器化部署           含 README 和 .gitignore
```

---

## 二、预备知识补充（15分钟速通）

进入 Step 0a 前，先补齐 6 个必须用到但你目前不熟的概念。

### 1. `if __name__ == "__main__"`

**是什么**：当 Python 文件被直接运行时，`__name__` 变量的值是 `"__main__"`；当它被其他文件导入时，`__name__` 是文件名。

```python
# demo.py
def main():
    print("程序运行了")

if __name__ == "__main__":
    main()
```

**为什么需要**：FastAPI 的启动入口 `uvicorn.run()` 必须写在这个判断后面，否则当你导入模型文件时，它会把不该运行的代码也跑一遍。

### 2. Python 类型注解

**是什么**：在函数参数和返回值后面加类型标记，方便编辑器检查错误，Pydantic 模型的基础。

```python
def add(a: int, b: int) -> str:
    return f"结果是：{a + b}"

# 调用时如果传字符串，编辑器会警告，但仍然能运行
```

**为什么需要**：FastAPI 的 Pydantic 模型就是靠类型注解来自动校验数据的。你写了 `age: int`，前端传 `"abc"` 会被自动拦截。

### 3. `try/except` 异常处理

**是什么**：捕捉程序运行时可能出现的错误，不让程序直接崩溃。

```python
try:
    # 可能出错的代码
    number = int(input("输入数字："))
    result = 100 / number
except ValueError:
    print("你输入的不是数字")
except ZeroDivisionError:
    print("不能除以0")
else:
    print(f"结果是：{result}")
finally:
    print("无论如何都会执行")
```

**为什么需要**：数据库连接失败、文件找不到、前端传了非法参数——这些都要用 try/except 兜住，返回友好错误信息而不是让服务器崩溃。

### 4. `async/await` 概念（会看不代表会写）

**是什么**：让程序在等待（比如等数据库返回结果）的时候，先去执行别的代码，不阻塞。

```python
import asyncio

async def fetch_data():
    print("开始请求数据...")
    await asyncio.sleep(2)    # 模拟等待网络响应
    print("数据回来了")
    return {"name": "张三"}

async def main():
    # 同时发两个请求，总耗时约2秒而不是4秒
    result1, result2 = await asyncio.gather(
        fetch_data(),
        fetch_data()
    )
    print(result1, result2)

asyncio.run(main())
```

**为什么需要**：FastAPI 的路由函数默认就是 `async def`。当你的接口要查数据库时，`await db_query()` 不会卡住服务器处理其他请求。**初始阶段你只需要记住"写路由用 `async def`，操作数据库前加 `await`"即可。**

### 5. `pip` 和虚拟环境

**是什么**：
- `pip install 包名` — 安装 Python 第三方包
- `python -m venv venv` — 创建虚拟环境（隔离项目的依赖，不污染全局）

**为什么需要**：不同项目依赖的版本可能冲突（项目一要 FastAPI 0.100，项目二要 0.110），虚拟环境把它们隔离开。

**基础操作**（只需记住这 3 条命令）：
```bash
python -m venv venv          # 创建虚拟环境（执行一次）
source venv/bin/activate     # 激活虚拟环境（Mac/Linux）
venv\Scripts\activate        # 激活虚拟环境（Windows）
pip install -r requirements.txt  # 根据清单安装所有依赖
```

### 6. 列表推导式（你已掌握）

**不重复讲。** 你会在 Step 2 用它简化查询结果处理。

---

### 前置知识小结

以上 6 个概念**不需要全部精通再开始**。核心要求：
- `if __name__`：知道为什么要写
- 类型注解：能看懂 `def func(x: int) -> str:` 的语法
- `try/except`：知道基本写法
- `async/await`：记住"FastAPI 路由用 `async def`，数据库操作用 `await`"
- 虚拟环境：记住那 3 条命令，动手前执行一遍

**开始项目一后如果遇到不理解的知识点，在当前步骤笔记里记录，我会在每步结束时帮你巩固。**

---

## 三、Step 0a：准备阶段（0.5天）

### 目标

所有开发环境就绪，第一次 `git commit` 成功。

### 3.1 环境状态（已完成确认）

| 工具 | 版本 | 状态 |
|------|------|------|
| Python | 3.13.4 | ✅ |
| Node.js | 24.15.0 | ✅ |
| Git | 2.54.0.windows.1 | ✅ |
| Docker | 29.4.3 | ✅ |

### 3.2 VSCode 插件安装

打开 VSCode → 扩展（Ctrl+Shift+X），搜索并安装：

| 插件 | 用途 | 必装 |
|------|------|------|
| **Python**（微软官方） | Python 智能提示、调试、运行 | ✅ |
| **Pylance** | Python 类型检查、自动补全 | ✅ |
| **Vue - Official** | Vue 单文件组件语法高亮 | ✅ |
| **REST Client** | 在 VSCode 里直接调试 HTTP 接口 | ✅ |
| Prettier - Code formatter | 代码自动格式化 | 推荐 |
| GitLens | 查看 Git 历史、代码作者 | 推荐 |
| Error Lens | 错误信息直接显示在行尾 | 推荐 |

### 3.3 Git 配置

```bash
# 配置用户名和邮箱（第一次用 Git 必须做）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 检查配置
git config --list

# 可选：配置 SSH 密钥（提交到 GitHub 不用输密码）
# 按三次回车生成默认密钥
ssh-keygen -t ed25519 -C "你的邮箱"
# 查看公钥，复制后添加到 GitHub Settings → SSH and GPG keys
cat ~/.ssh/id_ed25519.pub
```

### 3.4 创建项目仓库

```bash
# 回到项目根目录
cd c:/Users/PlusLcn/Desktop/python/ai学习规划/项目一

# 初始化 Git 仓库
git init

# GitHub 上新建一个空仓库（不要勾选 README/.gitignore），然后：
git remote add origin git@github.com:你的用户名/student-management.git

# 第一次提交
git add .
git commit -m "init: 项目一初始化"
git push -u origin main
```

### 3.5 MySQL 启动方案（二选一）

#### 选项 A：使用 Docker（推荐，省去本地安装的坑）

```bash
# 拉取 MySQL 8.0 镜像并启动
docker run --name student-mysql \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=student_db \
  -p 3306:3306 \
  -d mysql:8.0

# 验证是否启动成功
docker ps

# 连接测试（用 VSCode 的 SQL 插件或命令行）
docker exec -it student-mysql mysql -uroot -proot123
```

#### 选项 B：本地安装 MySQL 8.0

1. 去 https://dev.mysql.com/downloads/installer/ 下载安装包
2. 安装时选 Developer Default
3. 记住 root 密码（设为 `root123` 或自己记一个）
4. 验证：打开 MySQL 8.0 Command Line Client

---

## 四、Step 0b：设计阶段（0.5天）

### 4.1 项目目录结构（最终完整形态）

```
项目一/
├── backend/                    # FastAPI 后端项目
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # 应用入口，路由注册
│   │   ├── database.py        # 数据库连接配置
│   │   ├── models/            # SQLAlchemy ORM 模型
│   │   │   ├── __init__.py
│   │   │   └── student.py     # Student 数据表模型
│   │   ├── schemas/           # Pydantic 数据校验模型（请求/响应）
│   │   │   ├── __init__.py
│   │   │   └── student.py     # StudentCreate / StudentResponse 等
│   │   └── routers/           # 路由（API 接口）
│   │       ├── __init__.py
│   │       └── students.py    # 学生信息的 CRUD 接口
│   ├── requirements.txt       # Python 依赖清单
│   └── Dockerfile             # 后端 Docker 镜像配置
├── frontend/                  # Vue3 前端项目
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── api/
│   │   │   └── student.js    # 封装 Axios 调后端接口
│   │   ├── views/
│   │   │   └── StudentView.vue    # 主页面（包含表格+表单）
│   │   ├── components/
│   │   │   ├── StudentTable.vue   # 学生列表表格组件
│   │   │   ├── StudentForm.vue    # 新增/编辑表单组件
│   │   │   └── StudentDialog.vue  # 删除确认弹窗
│   │   └── router/
│   │       └── index.js
│   ├── package.json
│   └── Dockerfile             # 前端 Docker 镜像配置
├── docs/                      # 项目文档
│   ├── api-spec.md            # API 接口规范
│   ├── db-design.md           # 数据库设计
│   └── error-log.md           # 错误日志
├── .gitignore                 # 不提交到 Git 的文件清单
└── README.md                  # 项目说明
```

### 4.2 数据库设计（Student 表）

```sql
-- 数据库名：student_db
-- 字符集：utf8mb4（支持中文和 emoji）

CREATE TABLE students (
    id          INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    name        VARCHAR(50) NOT NULL COMMENT '姓名',
    age         INT NOT NULL COMMENT '年龄',
    gender      ENUM('男', '女', '其他') DEFAULT '其他' COMMENT '性别',
    grade       VARCHAR(20) NOT NULL COMMENT '年级/班级',
    phone       VARCHAR(20) COMMENT '手机号',
    email       VARCHAR(100) COMMENT '邮箱',
    address     VARCHAR(200) COMMENT '住址',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '学生信息表';
```

**设计理由：**

| 字段 | 为什么加 | 后续扩展 |
|------|---------|---------|
| `id` | 每张表都需要唯一主键 | 不变 |
| `name` | 学生的基本标识 | 可考虑拆 first_name/last_name |
| `age` | 最常见的查询条件之一 | 可加 birthday 替代（更精确） |
| `gender` | 管理系统的常规字段 | ENUM 限制可选值，减少脏数据 |
| `grade` | 按班级管理是常见需求 | 后续可拆成独立班级表 |
| `phone/email` | 联系信息 | 可在 Step 5 加上 |
| `address` | 选填字段，展示如何处理可选字段 | 不变 |
| `created_at/updated_at` | 每张表都应该有，排序和追踪用 | 所有表通用 |

### 4.3 API 接口规范

基础 URL：`http://localhost:8000/api/v1`

#### 5 个核心接口

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | `/students/` | 获取学生列表（含分页） | 无 | `{items: [...], total: N}` |
| GET | `/students/{id}` | 获取单个学生详情 | 无 | `{id, name, age, ...}` |
| POST | `/students/` | 新增学生 | `StudentCreate` | `StudentResponse` |
| PUT | `/students/{id}` | 更新学生信息 | `StudentUpdate` | `StudentResponse` |
| DELETE | `/students/{id}` | 删除学生 | 无 | `{message: "删除成功"}` |

#### 请求/响应格式示例

**POST /students/ 请求体：**
```json
{
    "name": "张三",
    "age": 20,
    "gender": "男",
    "grade": "计算机1班",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "address": "北京市海淀区"
}
```

**GET /students/ 响应体：**
```json
{
    "items": [
        {
            "id": 1,
            "name": "张三",
            "age": 20,
            "gender": "男",
            "grade": "计算机1班",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "address": "北京市海淀区",
            "created_at": "2026-05-31T10:00:00",
            "updated_at": "2026-05-31T10:00:00"
        }
    ],
    "total": 1
}
```

**统一错误响应（所有接口通用）：**
```json
{
    "detail": "错误描述信息"
}
```

**为什么这样设计：**

| 设计决策 | 理由 |
|---------|------|
| 前缀 `/api/v1` | 后续升级接口时（v2）不影响已有调用方 |
| 统一用复数 `/students/` | RESTful 规范，资源名用复数 |
| `PUT` 全量更新 | 比 PATCH 简单，初学阶段够用 |
| 分页参数默认值 | 避免一次返回上万条数据 |
| 统一错误格式 | 前端处理错误时不用猜格式 |

### 4.4 前端原型

#### 页面布局总览

```
+----------------------------------------------------------+
|  学生管理系统  [新增学生]                                    |
+----------------------------------------------------------+
| 搜索框 [______] [搜索]                                     |
+----------------------------------------------------------+
| 编号 | 姓名 | 年龄 | 性别 | 班级   | 操作                  |
|  1   | 张三  | 20   | 男   | 计算机1班 | [编辑] [删除]    |
|  2   | 李四  | 21   | 女   | 计算机2班 | [编辑] [删除]    |
|  3   | 王五  | 19   | 男   | 计算机1班 | [编辑] [删除]    |
+----------------------------------------------------------+
| 共 10 条  < 1 2 3 4 >                                     |
+----------------------------------------------------------+
```

#### 交互流程

```mermaid
sequenceDiagram
    participant 用户
    participant 列表页
    participant 弹窗
    participant 后端API
    participant 数据库

    Note over 用户,数据库: 查看列表（GET）
    用户->>列表页: 打开页面
    列表页->>后端API: GET /api/v1/students/
    后端API->>数据库: SELECT * FROM students
    数据库-->>后端API: 返回数据
    后端API-->>列表页: 返回JSON
    列表页-->>用户: 渲染表格

    Note over 用户,数据库: 新增学生（POST）
    用户->>列表页: 点击"新增学生"
    列表页->>弹窗: 打开表单弹窗
    用户->>弹窗: 填写信息，点"保存"
    弹窗->>后端API: POST /api/v1/students/ {name, age, ...}
    后端API->>数据库: INSERT INTO students ...
    数据库-->>后端API: 成功
    后端API-->>弹窗: 返回新学生数据
    弹窗-->>列表页: 关闭弹窗，刷新列表

    Note over 用户,数据库: 编辑学生（PUT）
    用户->>列表页: 点击某行的"编辑"
    列表页->>弹窗: 打开表单弹窗（回填数据）
    用户->>弹窗: 修改信息，点"保存"
    弹窗->>后端API: PUT /api/v1/students/{id} {name, age, ...}
    后端API->>数据库: UPDATE students SET ... WHERE id=?
    数据库-->>后端API: 成功
    后端API-->>弹窗: 返回更新后数据
    弹窗-->>列表页: 关闭弹窗，刷新列表

    Note over 用户,数据库: 删除学生（DELETE）
    用户->>列表页: 点击某行的"删除"
    列表页->>用户: 确认框 "确定删除张三？"
    用户->>列表页: 确认
    列表页->>后端API: DELETE /api/v1/students/{id}
    后端API->>数据库: DELETE FROM students WHERE id=?
    数据库-->>后端API: 成功
    后端API-->>列表页: {message: "删除成功"}
    列表页-->>用户: 刷新列表
```

#### 组件划分

| 组件 | 职责 | 状态管理 |
|------|------|---------|
| `StudentView.vue` | 页面容器，协调子组件 | 管理 studentList 列表数据 |
| `StudentTable.vue` | 展示表格，触发的编辑/删除事件 | 只展示数据，通过 emit 通知父组件 |
| `StudentForm.vue` | 新增/编辑表单，表单验证 | 通过 props 接收初始值，emit 提交事件 |
| `StudentDialog.vue` | 删除确认弹窗 | 接收学生名称和 ID |

### 4.5 笔记模板

每完成一步，我会按此模板生成笔记，追加到 `docs/step-N-notes.md`：

```markdown
# Step N：{步骤名称}

## 用时
{实际用时} / {预估用时}

## 本步做了什么
{一句话说明本步目标}

## 执行的关键命令
| 命令 | 解释 | 为什么这样写 |
|------|------|-------------|
| `python -m venv venv` | 创建虚拟环境 | 隔离项目依赖，避免版本冲突 |
| ... | ... | ... |

## 核心代码
```python
# 只放关键代码段，不放所有代码
```

## 犯的错 & 解决方法
| 错误信息 | 原因 | 解决方式 |
|---------|------|---------|
| ... | ... | ... |

## 本步知识点归纳
- {知识点1}：{一句话解释}
- {知识点2}：{一句话解释}

## 本步完成后能回答的问题
Q: {面试常见问题}
A: {一句话答案}

## 下一步做什么
{下一目标}
```

### 4.6 错误日志模板

创建 `docs/error-log.md`，每遇到一个错误就追加一条：

```markdown
# 错误日志

## 2026-05-31

### 1. {错误标题}
- **场景**：执行什么操作时出现
- **错误信息**：完整的报错信息
- **原因**：根本原因
- **解法**：怎么解决的
- **预防**：以后如何避免
```

---

## 五、Step 1：FastAPI 写 CRUD 接口（3-4天）

### 目标

用 FastAPI 写 5 个学生管理的 RESTful 接口，不连接数据库，数据存内存，返回 JSON。

### 要问我的问题

1. "写一个 FastAPI 项目的基本结构，从 main.py 开始"
2. "解释 Pydantic 模型怎么定义，写一个 StudentCreate 和 StudentResponse"
3. "写 5 个路由：增删改查+列表，数据先放在内存列表里"
4. "讲一下 FastAPI 的 HTTP 方法（GET/POST/PUT/DELETE）区别"
5. "怎么在 VSCode 中运行 FastAPI 并测试接口"

### 学到的知识点

- FastAPI 应用创建和运行（`uvicorn`）
- 路由装饰器 `@app.get/post/put/delete`
- Pydantic 模型定义和自动校验
- 路径参数和查询参数的区别（`{id}` vs `?page=1&size=10`）
- 使用 REST Client 插件调试接口

### 验证标准

- [ ] `uvicorn app.main:app --reload` 启动后无报错
- [ ] 用 REST Client 或浏览器访问 `http://localhost:8000/docs` 能看到 Swagger 文档
- [ ] 发 POST 请求成功创建学生
- [ ] 发 GET 请求能查到刚创建的学生
- [ ] 发 PUT 请求能修改学生信息
- [ ] 发 DELETE 请求能删除学生

---

## 六、Step 2：连接 MySQL 数据库（3-4天）

### 目标

把 Step 1 内存中的数据改成从 MySQL 读写。

### 要问我的问题

1. "写 SQLAlchemy 连接 MySQL 的配置代码（database.py）"
2. "写 Student 的 SQLAlchemy ORM 模型"
3. "把内存 CRUD 改成数据库 CRUD"
4. "解释 SQLAlchemy 的 Session、Query、commit、rollback"
5. "用 Docker 启动 MySQL 并连接到 FastAPI"

### 学到的知识点

- SQLAlchemy `create_engine` / `sessionmaker` / `SessionLocal`
- ORM 模型定义（`Column`, `Integer`, `String`, `DateTime`）
- CRUD 操作：`db.add()` / `db.commit()` / `db.refresh()` / `db.query().all()` / `db.delete()`
- 数据库连接字符串格式（`mysql+pymysql://user:password@host:port/db`）

### 验证标准

- [ ] 启动后接口仍能正常工作
- [ ] 新增的学生重启后数据不丢失
- [ ] 在 MySQL 命令行查询能看到数据

---

## 七、Step 3：Vue3 写前端页面（3-5天）

### 目标

写一个完整的 Vue3 前端，接入后端 API，实现学生信息管理界面。

### 要问我的问题

1. "用 Vite 创建 Vue3 项目的命令"
2. "安装 Element Plus 并写一个表格页面"
3. "写 Axios 配置和 API 调用封装"
4. "写新增/编辑表单弹窗"
5. "把增删改查全部串起来"
6. "跨域问题（CORS）怎么在 FastAPI 端解决"

### 学到的知识点

- Vite 创建和管理 Vue3 项目
- Element Plus 组件使用（`el-table`, `el-form`, `el-dialog`, `el-pagination`）
- Axios 请求封装和后端 API 对接
- Vue3 组合式 API（`ref`, `reactive`, `computed`, `onMounted`）
- 跨域问题的原因和解决方法

### 验证标准

- [ ] 前后端同时运行，页面能显示学生列表
- [ ] 点"新增"能弹窗填表单，保存后列表刷新
- [ ] 点"编辑"能回填数据，修改后列表刷新
- [ ] 点"删除"有确认弹窗，确认后列表刷新

---

## 八、Step 4：部署上线（2-3天）

### 目标

把项目打包成 Docker 镜像，能在一台干净服务器上运行。

### 要问我的问题

1. "把项目部署到 Linux 服务器的完整步骤"
2. "写 Dockerfile（前端和后端各一个）"
3. "写 docker-compose.yml（含 MySQL）"
4. "Nginx 做反向代理的配置"

### 学到的知识点

- Dockerfile 编写（`FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`）
- Docker Compose 编排多容器
- Nginx 反向代理配置
- Linux 基本操作（`ssh`, `scp`, `systemctl`, `docker`）

### 验证标准

- [ ] `docker-compose up` 启动后所有服务正常运行
- [ ] 通过浏览器访问服务器 IP 能看到系统正常运行
- [ ] `docker-compose down` 能正常停止

---

## 九、Step 5：加功能强化简历（选做，3-4天）

### 目标

给系统加上认证、搜索、导出功能，看起来像企业级项目。

### 要问我的问题

1. "用 JWT 做登录认证"
2. "加搜索和分页查询"
3. "加 Excel 导出功能"

### 学到的知识点

- JWT 的 token 生成和验证
- 依赖注入 `Depends()` 做权限校验
- 模糊查询 (LIKE)
- Excel 文件生成和下载

### 验证标准

- [ ] 需要登录才能访问学生管理
- [ ] 搜索框输入关键字能过滤结果
- [ ] 表格支持分页
- [ ] 能导出 Excel

---

## 十、笔记模板

> 每步完成后，我会按此格式生成独立笔记文件到 `docs/step-N-notes.md`

### 文件命名规则

```
docs/
├── step-0a-notes.md      # 准备阶段笔记
├── step-0b-notes.md      # 设计阶段笔记
├── step-1-notes.md       # Step 1 笔记
├── step-2-notes.md       # Step 2 笔记
├── step-3-notes.md       # Step 3 笔记
├── step-4-notes.md       # Step 4 笔记
├── step-5-notes.md       # Step 5 笔记（选做）
└── error-log.md          # 错误日志（贯穿全程）
```

### 笔记内容结构

每篇笔记包含以下段落：

1. **本步用时** — 计划用时 vs 实际用时
2. **做了什么事** — 一句话目标和本步完成情况
3. **命令执行记录** — 每一条关键命令、作用、为什么用这个而不是别的方式
4. **核心代码段** — 只放提纲挈领的代码片段，不是全文粘贴
5. **犯错记录** — 报错信息、原因、解决方式
6. **知识点归纳** — 本步学到的所有新概念，用一句话解释
7. **面试题库** — 本步涉及的知识点在面试中可能被怎么问
8. **下一步预告** — 接下来要做什么，提前心理准备

---

## 十一、错误日志模板

文件：`docs/error-log.md`

```markdown
# 错误日志 — 全栈学生管理系统

> 记录项目中遇到的所有报错和解决方案
> 格式：每一条独立条目，按时间排序

---

## 2026-05-31

### 1. [标题：一句话描述问题]

- **场景**：在做什么操作时报错
- **报错信息**：

  ```
  完整的报错信息
  ```

- **原因分析**：为什么会出现这个错误
- **解决方案**：怎么修复的，具体命令或代码修改
- **预防措施**：后续如何避免同样错误

---

## 使用说明

- 每次遇到报错立即记录，不要等"做完再记"
- 复制完整的报错信息，不要缩写
- 解决方案要落实到具体操作（命令/代码行）
- 如果同一个错误反复出现，在原因分析里补充"根源"
```

---

## 十二、前置知识自测表

**进入 Step 0a 前，对照检查是否具备以下条件：**

### 环境条件

- [ ] Python 3.10+ 已安装（✅ 3.13.4）
- [ ] Node.js 16+ 已安装（✅ 24.15.0）
- [ ] Git 已安装并配置了 user.name 和 user.email（✅ 2.54.0）
- [ ] Docker 已安装（✅ 29.4.3）
- [ ] VSCode 已安装 Python / Pylance / Vue - Official / REST Client 插件

### 概念条件（以下 6 个不需要精通，但要见过）

- [ ] 知道 `if __name__ == "__main__"` 什么时候用
- [ ] 能看懂 `def add(a: int, b: int) -> str:`
- [ ] 能写一个 `try/except` 捕获特定类型的错误
- [ ] 记住"FastAPI 路由用 `async def`，数据库操作用 `await`"
- [ ] 记住虚拟环境的三条命令（创建、激活、装包）
- [ ] 能写列表推导式（✅）

### 账号条件

- [ ] GitHub 账号（注册好）
- [ ] （可选但不影响起步）GitHub 已配好 SSH 密钥

---

## 文件清单（项目一结束后产物）

```
项目一/
├── backend/                    # FastAPI 后端源码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/student.py
│   │   ├── schemas/student.py
│   │   └── routers/students.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Vue3 前端源码
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── api/student.js
│   │   ├── views/StudentView.vue
│   │   ├── components/
│   │   │   ├── StudentTable.vue
│   │   │   ├── StudentForm.vue
│   │   │   └── StudentDialog.vue
│   │   └── router/index.js
│   ├── package.json
│   └── Dockerfile
├── docs/                       # 项目文档 + 笔记
│   ├── api-spec.md
│   ├── db-design.md
│   ├── error-log.md
│   ├── step-0a-notes.md
│   ├── step-0b-notes.md
│   ├── step-1-notes.md
│   ├── step-2-notes.md
│   ├── step-3-notes.md
│   └── step-4-notes.md
├── .gitignore
└── README.md
```

---

## 各步骤用时和精力分布

| 步骤 | 预估用时 | 周末建议 | 工作日建议 |
|------|---------|---------|-----------|
| 预备知识 | 15分钟 | - | 一次过完 |
| Step 0a：准备 | 0.5天 | 集中完成 | - |
| Step 0b：设计 | 0.5天 | 接着Step 0a | - |
| Step 1：FastAPI | 3-4天 | 集中攻接口 | 每天写1-2个路由 |
| Step 2：数据库 | 3-4天 | 集中改CRUD | 每天改1-2个接口 |
| Step 3：Vue3 | 3-5天 | 集中写页面 | 每天写1个组件 |
| Step 4：部署 | 2-3天 | 周末集中 | - |
| Step 5：强化 | 3-4天选做 | 有余力再做 | - |

> **核心原则**：工作日 2 小时只做一件事，周末 4-6 小时整合推进。
> **遇到问题卡住超过 15 分钟，直接问我，不要自己硬搜。**
