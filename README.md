# 学生信息管理系统

一个前后端分离的学生信息管理平台：登录后可以对学生信息做增删改查、按姓名搜索、分页浏览，并一键导出 Excel。

后端 FastAPI 提供 RESTful API，前端 Vue 3 + Element Plus，数据存 MySQL，三服务用 Docker Compose 一键编排。

---

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | Python 3.13 · FastAPI · SQLAlchemy 2.0 · Pydantic |
| 认证 | JWT（python-jose）· bcrypt 密码哈希（passlib） |
| 数据库 | MySQL 8.0 · PyMySQL 驱动 |
| 前端 | Vue 3 · Vite · Element Plus · axios · Vue Router |
| 导出 | openpyxl（服务端生成）· Blob 流式下载 |
| 部署 | Docker 多阶段构建 · Docker Compose · Nginx |

---

## 架构

```
                     浏览器
                        │
                        ▼
        ┌───────────────────────────────────┐
        │  student-frontend  (Nginx, :80)   │
        │                                   │
        │   /       → 静态文件 dist/         │
        │   /api/   → http://backend:8000   │
        └───────────────┬───────────────────┘
                        │  Docker 内部网络（服务名寻址）
                        ▼
        ┌───────────────────────────────────┐
        │  student-backend   (Uvicorn, :8000)
        │                                   │
        │   JWT 校验 → 业务逻辑 → ORM 查询   │
        └───────────────┬───────────────────┘
                        │  mysql+pymysql
                        ▼
        ┌───────────────────────────────────┐
        │  student-mysql     (MySQL 8.0)    │
        │   volume: mysql_data              │
        └───────────────────────────────────┘
```

**前端和 API 同源**：Nginx 既发静态文件，又把 `/api` 转发给后端。浏览器只跟一个地址打交道，所以后端不需要开 CORS —— `main.py` 里的 CORS 中间件是**注释掉的**，这不是遗漏，是架构决定的。

---

## 功能

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/v1/auth/register` | 注册（密码 bcrypt 加盐哈希后入库） |
| `POST` | `/api/v1/auth/login` | 登录，返回 JWT token |
| `GET` | `/api/v1/students/` | 学生列表，支持 `page` / `size` / `keyword` |
| `GET` | `/api/v1/students/{id}` | 学生详情 |
| `POST` | `/api/v1/students/` | 新增学生 |
| `PUT` | `/api/v1/students/{id}` | 更新学生 |
| `DELETE` | `/api/v1/students/{id}` | 删除学生 |
| `GET` | `/api/v1/students/export/excel` | 导出全部学生为 xlsx |

除注册、登录外，**所有接口都要求 `Authorization: Bearer <token>`**，校验失败返回 401。

启动后端后可访问 `/docs` 查看自动生成的 Swagger 文档，也可以用 `backend/test.http` 逐个试接口。

### 前端路由保护

```
/login   →  登录页
/        →  学生管理页（meta.requiresAuth = true）
```

两道防线：

- **Vue Router 导航守卫**：访问 `/` 时没有 token 就跳 `/login`；已登录再访问 `/login` 则跳回 `/`
- **axios 请求拦截器**：每次请求前自动从 `localStorage` 取 token 塞进 `Authorization` 头

前端拦的是体验（不让用户进到空白页），后端拦的才是安全（没 token 一律 401）—— 前端守卫可以绕过，后端校验绕不过。

---

## 快速开始

需要 Docker Desktop 已启动。

```bash
git clone https://github.com/PLusLcn/student-management.git
cd student-management

docker compose up -d
```

打开 **http://127.0.0.1:8081**，先注册一个账号再登录。

### 常用命令

```bash
docker compose ps                     # 看三个容器状态
docker compose logs -f backend        # 看后端日志
docker compose down                   # 停止（保留数据）
docker compose down -v                # 停止并删除数据库数据 ⚠️ 不可逆
docker compose up -d --build          # 改了代码后重建
```

### 表结构

建表由 SQLAlchemy 在应用启动时完成（`lifespan` 里调 `Base.metadata.create_all`），不需要手动执行 SQL。两张表：

- `students` —— 姓名、年龄、性别、班级、电话、邮箱、地址、创建/更新时间
- `users` —— 用户名、密码哈希、创建时间

字段设计详见 [`docs/db-design.md`](docs/db-design.md)。

---

## 设计取舍

### 用 healthcheck 控制启动顺序

MySQL 容器"启动完成"和"能接受连接"是两回事。如果 backend 只写 `depends_on: mysql`，它会在 MySQL 还在初始化时就发起连接，然后崩溃退出。

所以给 MySQL 加了 healthcheck（`mysqladmin ping`），backend 用 `condition: service_healthy` —— 等到数据库真的能 ping 通了才启动。这是 Compose 里控制顺序的正确写法。

### 密码存哈希，不存明文

`auth.py` 用 passlib 的 bcrypt 做哈希，bcrypt 自带随机盐，所以相同的密码每次哈希结果也不同。登录时用 `verify_password` 比对，数据库里永远看不到原始密码。

### Excel 在服务端生成

导出走 openpyxl 在服务端拼好 xlsx，再用 `StreamingResponse` 推给前端，前端拿 `responseType: 'blob'` 接收后触发下载。

没有选前端生成（如 SheetJS）的原因是：**数据在后端，让数据靠近处理它的地方**。前端只需处理一个二进制流，不用把所有学生数据先拉到浏览器再拼表。

### 前端多阶段构建

编译 Vue 需要 Node，但跑起来只需要 Nginx 发静态文件。所以镜像分两阶段：Node 阶段 `npm ci && npm run build` 产出 `dist/`，Nginx 阶段只 `COPY` 这一个目录，**最终镜像里没有 Node**。

### SPA 路由回退

Nginx 里配了 `try_files $uri $uri/ /index.html`。前端用的是 `createWebHistory`（真实路径，没有 `#`），刷新 `/login` 时服务器上并不存在这个文件，会 404。回退到 `index.html` 后由 Vue Router 接管路由。

---

## 已知限制

### 密钥和密码硬编码

`auth.py` 里 `SECRET_KEY` 是写死的字符串，数据库密码 `root123` 同时出现在 `docker-compose.yml` 和 `database.py` 的默认值里。

正确做法是从环境变量读取（`os.getenv("SECRET_KEY")`），本地用 `.env`、部署时由平台注入。项目二的同类配置已经改成这种写法，这里**尚未回改**。

### 没有 RBAC

当前是"登录即可用"——任何注册过的用户权限完全相同，没有角色区分。

`verify_token` 只回答"你是谁"（返回 user_id），不回答"你能不能做这件事"。要加权限控制需要在 User 表加角色字段，并让依赖项同时校验角色。

### 其他

- **更新是全量覆盖**：`StudentUpdate` 要求前端传完整字段，没传的会变 `None`，不是 PATCH 语义的部分更新
- **导出不分页**：`/students/export/excel` 一次查全表，数据量大时会占内存
- **`verify_token` 重复定义**：`students.py` 和 `export.py` 里各写了一份，应该抽成公共依赖（`Depends`）
- **没有数据库迁移工具**：靠 `create_all` 建表，改了模型字段不会自动同步到已有表，正式项目应该上 Alembic
- **`test.http` 需手动替换 token**：登录拿到的 token 要复制进去才能试受保护接口

---

## 项目结构

```
项目一/
├── backend/
│   ├── app/
│   │   ├── main.py             FastAPI 入口 + 建表 + 路由注册
│   │   ├── database.py         引擎、会话、Base、get_db 依赖
│   │   ├── auth.py             JWT 签发/校验、bcrypt 哈希
│   │   ├── models/             ORM 模型（student / user）
│   │   ├── schemas/            Pydantic 请求/响应模型
│   │   └── routers/            接口层（students / auth / export）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── test.http               接口调试用例
├── frontend/
│   ├── src/
│   │   ├── api/                axios 实例（auth.js / student.js）
│   │   ├── views/              LoginView.vue / StudentView.vue
│   │   ├── components/         StudentForm.vue / StudentTable.vue
│   │   └── router/index.js     路由 + 导航守卫
│   ├── nginx.conf              静态文件 + 反向代理
│   └── Dockerfile              多阶段构建
├── docs/
│   ├── api-spec.md             接口规格
│   ├── db-design.md            表结构设计
│   ├── error-log.md            踩坑记录
│   └── day-1 ~ day-5 notes     分日开发笔记
└── docker-compose.yml
```
