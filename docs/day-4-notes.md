# Day 4：功能增强 + Docker 部署

> 全栈学生管理系统 ｜ 学习日期：2026-06-04

---

## 目录

- [一、Step 4 概述](#一step-4-概述)
- [二、搜索功能](#二搜索功能)
- [三、删除确认弹窗](#三删除确认弹窗)
- [四、表单验证](#四表单验证)
- [五、Docker 部署](#五docker-部署)
- [六、完整知识点归纳](#六完整知识点归纳)
- [七、项目结构（最终状态）](#七项目结构最终状态)
- [八、错误记录](#八错误记录)
- [九、面试题](#九面试题)

---

## 一、Step 4 概述

### 做了什么

1. 搜索功能 — 按姓名关键字过滤学生列表
2. 删除确认弹窗 — 防止误删
3. 表单验证 — 必填字段、手机号格式、邮箱格式
4. Docker 部署 — 编写 Dockerfile、docker-compose、Nginx 配置

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/routers/students.py` | **修改** | 列表接口加 keyword 参数和模糊查询 |
| `backend/app/database.py` | **修改** | DATABASE_URL 改为环境变量可配置 |
| `backend/Dockerfile` | **新建** | 后端 Docker 镜像 |
| `frontend/src/api/student.js` | **修改** | baseURL 改为相对路径 `/api/v1` |
| `frontend/src/App.vue` | **修改** | 搜索框、删除确认、表单验证 |
| `frontend/vite.config.js` | **修改** | 加 dev 代理 `/api` → `localhost:8001` |
| `frontend/Dockerfile` | **新建** | 前端 Docker 镜像（多阶段构建） |
| `frontend/nginx.conf` | **新建** | Nginx 反向代理配置 |
| `backend/app/main.py` | **修改** | 注释掉 CORS 中间件（生产用 Nginx） |
| `docker-compose.yml` | **新建** | 编排 MySQL + 后端 + 前端 |

---

## 二、搜索功能

### 原理

前端传一个 `keyword` 参数给后端，后端在 SQL 查询中加 `WHERE name LIKE '%关键字%'` 条件。

### 后端改动

```python
@router.get("/students/")
def list_students(page: int = 1, size: int = 10, keyword: str = "", db: Session = Depends(get_db)):
    query = db.query(Student)
    if keyword:
        query = query.filter(Student.name.contains(keyword))   # LIKE '%keyword%'
    items = query.offset((page - 1) * size).limit(size).all()
    total = query.count()
    return {"items": [StudentResponse.model_validate(s) for s in items], "total": total}
```

- `keyword: str = ""` — 可选参数，默认空字符串，不传不影响
- `Student.name.contains(keyword)` — SQLAlchemy 的模糊查询，对应 SQL `name LIKE '%keyword%'`
- `.count()` 放在 `filter` 之后、`offset/limit` 之前，统计的是**过滤后的总数**

### 前端改动

**api/student.js** — 加 keyword 参数：
```javascript
export const listStudents = (page, size, keyword) =>
    api.get('/students/', { params: { page, size, keyword } })
```

**App.vue** — 加搜索框和 search() 函数：
```vue
<script setup>
const keyword = ref('')

const search = () => {
  page.value = 1           // 搜索时回到第一页
  loadList()
}

const loadList = async () => {
  const res = await listStudents(page.value, size.value, keyword.value)
  studentList.value = res.data.items
  total.value = res.data.total
}
</script>

<template>
  <div style="margin-bottom: 10px; display: flex; gap: 10px">
    <el-input v-model="keyword" placeholder="搜索姓名" style="width: 200px" clearable />
    <el-button type="primary" @click="search">搜索</el-button>
  </div>
</template>
```

- `clearable` — 输入框右侧出现小叉，点击清空内容
- 搜索时重置 `page.value = 1`，避免翻到第3页搜索后列表为空

---

## 三、删除确认弹窗

### 为什么需要

用户点"删除"时直接调 API 删掉，误触无法恢复。加一个确认弹窗让用户二次确认。

### 实现

```vue
<script setup>
import { ElMessageBox } from 'element-plus'

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该学生吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteStudent(id)      // 用户点了确定才执行删除
    loadList()
  } catch {
    // 用户点了取消，什么都不做（必须 catch，否则控制台报错）
  }
}
</script>
```

- `ElMessageBox.confirm()` — 弹出一个确认对话框，返回 Promise
  - 点"确定" → Promise resolve → 执行删除
  - 点"取消" → Promise reject → 被 catch 捕获，无操作
- `type: 'warning'` — 弹窗图标显示为黄色警告样式

---

## 四、表单验证

### 原理

Element Plus 通过 `:rules` 绑定验证规则对象 + `formRef.value.validate()` 触发验证。

### 验证规则

```javascript
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入班级', trigger: 'blur' }],
  phone: [{
    pattern: /^1[3-9]\d{9}$/,          // 正则：1开头的11位手机号
    message: '手机号格式不正确',
    trigger: 'blur'
  }],
  email: [{
    type: 'email',                       // 内置 email 类型校验
    message: '邮箱格式不正确',
    trigger: 'blur'
  }]
}
```

### 在模板中绑定

```vue
<el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
  <el-form-item label="姓名" prop="name" required>
    <el-input v-model="form.name" />
  </el-form-item>
  <!-- prop="字段名" 告诉表单规则对应哪个字段 -->
</el-form>
```

- `:rules="rules"` — 绑定验证规则对象
- `prop="name"` — 指定该表单项对应 rules 中的哪个字段
- `required` — 在表头加红色星号（视觉提示，真正校验靠 rules）

### 在提交时触发验证

```javascript
const submitForm = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()       // 触发表单验证
    if (isEdit.value) {
      await updateStudent(editId.value, form.value)
    } else {
      await createStudent(form.value)
    }
    dialogVisible.value = false
    loadList()
  } catch {
    // 验证不通过，什么都不做（Element Plus 会自动显示错误信息）
  }
}
```

- `formRef.value.validate()` — 验证所有带 `prop` 的字段，全部通过才 resolve
- 验证不通过时自动在对应输入框下方显示 `message` 内容

### 规则类型总结

| 规则 | 写法 | 说明 |
|------|------|------|
| 必填 | `{ required: true }` | 字段不能为空 |
| 正则 | `{ pattern: /正则/ }` | 匹配自定义格式 |
| 内置类型 | `{ type: 'email' }` | element-plus 内置格式校验 |
| 长度 | `{ min: 3, max: 10 }` | 字符串长度范围 |
| 自定义 | `{ validator: (rule,val,cb) => {} }` | 函数自定义校验逻辑 |

---

## 五、Docker 部署

### 整体架构

```
                  ┌──────────────────────────┐
                  │   Nginx（前端）           │
                  │   localhost:8081          │
                  │   / → index.html          │
                  │   /api/ → proxy backend   │
                  └────────┬─────────────────┘
                           │ http://backend:8000/api/
                  ┌────────▼─────────────────┐
                  │   FastAPI（后端）          │
                  │   port 8000               │
                  │   DATABASE_URL env var    │
                  └────────┬─────────────────┘
                           │ mysql+pymysql://root:root123@mysql:3306
                  ┌────────▼─────────────────┐
                  │   MySQL 8.0               │
                  │   port 3306               │
                  │   volume: mysql_data      │
                  └──────────────────────────┘
```

### 5.1 后端 Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- `FROM python:3.13-slim` — 基于 Python 3.13 精简镜像，比完整版小很多
- `WORKDIR /app` — 设置工作目录，后续命令都在这个目录下执行
- `COPY requirements.txt .` — 先复制依赖文件（利用 Docker 缓存层，依赖没变就不重装）
- `RUN pip install` — 安装依赖
- `COPY . .` — 复制所有源码（这一层前面依赖没变就不会重新执行）
- `EXPOSE 8000` — 声明容器监听端口（仅文档作用）
- `CMD` — 启动命令

### 5.2 前端 Dockerfile（多阶段构建）

```dockerfile
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**为什么用多阶段构建？**

| 阶段 | 作用 | 产物 |
|------|------|------|
| `build` | 安装 node 依赖、编译前端代码 | `dist/` 目录（纯静态文件） |
| `nginx` | 把 dist 复制到 nginx 目录 | 最终镜像只有 nginx + 静态文件 |

**好处**：最终镜像只有几十 MB（Nginx），不会带上 node_modules（几百 MB）。

- `AS build` — 给阶段命名，后面用 `--from=build` 引用
- `npm ci` — 比 `npm install` 更快更严格（依赖锁定文件必须存在）
- `daemon off;` — Nginx 前台运行，否则容器启动后立即退出

### 5.3 Nginx 配置

```
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- `location /` — 前端静态文件，`try_files` 保证 SPA 路由刷新不 404
- `location /api/` — 反向代理到后端容器（`backend` 是 docker-compose 中的服务名）
- Docker Compose 内部网络通过**服务名**访问，不通过 IP

### 5.4 docker-compose.yml

```yaml
name: student-management
services:

  mysql:
    image: mysql:8.0
    container_name: student-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: student_db
    ports:
      - "3308:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  backend:
    build: ./backend
    container_name: student-backend
    environment:
      DATABASE_URL: mysql+pymysql://root:root123@mysql:3306/student_db
    ports:
      - "8000:8000"
    depends_on:
      mysql:
        condition: service_healthy

  frontend:
    build: ./frontend
    container_name: student-frontend
    ports:
      - "8081:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

**关键点：**

| 配置 | 作用 |
|------|------|
| `name: student-management` | 指定 compose 项目名，避免默认用目录名 |
| `volumes: mysql_data` | 数据持久化，compose down 后数据不丢 |
| `healthcheck` | MySQL 完全就绪后后端才启动 |
| `depends_on.condition: service_healthy` | 等待 MySQL 健康检查通过 |
| `DATABASE_URL: mysql+pymysql://root:root123@mysql:3306/student_db` | 连接串用服务名 `mysql`，端口 3306（容器内部端口） |

### 5.5 环境变量配置数据库连接

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3308/student_db")
```

- `os.getenv("DATABASE_URL", "默认值")` — 读取环境变量，没设置时用默认值
- **开发模式**：不设环境变量，连接 `localhost:3308`（宿主机 MySQL）
- **Docker 模式**：compose 传入 `DATABASE_URL`，连接 `mysql:3306`（容器内 MySQL）

### 5.6 Vite 代理（替代 CORS）

```javascript
// vite.config.js
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
})
```

- 开发时前端 `5173` → Vite 代理 → `8001`（后端），**同源**，不需要 CORS
- `baseURL: '/api/v1'`（相对路径），不再写 `http://localhost:8001/api/v1`

**两种部署模式对比：**

| | 开发模式（Dev） | Docker 模式（Prod） |
|---|---|---|
| 前端地址 | `localhost:5173` | `localhost:8081` |
| 后端地址 | `localhost:8001` | 容器内 `8000` |
| 跨域方案 | Vite 代理 | Nginx 反向代理 |
| CORS 中间件 | 需要（注释掉了，因为用 Vite 代理） | 不需要（同源） |
| MySQL 连接 | `localhost:3308` | `mysql:3306` |
| 启动方式 | 手动启动三个进程 | `docker-compose up` |

---

## 六、完整知识点归纳

### 搜索

| 概念 | 一句话解释 |
|------|-----------|
| `.contains()` | SQLAlchemy 模糊查询，生成 `LIKE '%keyword%'` |
| `.count()` | 统计查询结果总数（在 filter 之后、limit 之前） |
| `clearable` | Element Plus 输入框属性，加清除按钮 |
| `@click="search"` 重置页码 | 搜索时回到第一页，避免搜索结果为空 |

### 删除确认

| 概念 | 一句话解释 |
|------|-----------|
| `ElMessageBox.confirm()` | Element Plus 的确认对话框，返回 Promise |
| `try/catch` 包裹 | 用户点取消会 reject，必须 catch 防止控制台报错 |
| `type: 'warning'` | 弹窗图标样式 |

### 表单验证

| 概念 | 一句话解释 |
|------|-----------|
| `:rules` | 绑定验证规则对象到 el-form |
| `prop="字段名"` | 告诉表单该输入框对应 rules 中的哪个规则 |
| `required: true` | 必填校验 |
| `pattern: /正则/` | 自定义格式校验（如手机号） |
| `type: 'email'` | Element Plus 内置邮箱格式校验 |
| `formRef.value.validate()` | 手动触发表单校验，全部通过才 resolve |
| `trigger: 'blur'` | 失焦时触发校验 |

### Docker

| 概念 | 一句话解释 |
|------|-----------|
| `FROM` | 指定基础镜像 |
| `WORKDIR` | 设置容器内工作目录 |
| `COPY` | 从宿主机复制文件到镜像 |
| `RUN` | 在构建时执行命令（如 pip install） |
| `CMD` | 容器启动时执行的命令 |
| `EXPOSE` | 声明端口（仅文档作用） |
| 多阶段构建 | 先在一个镜像编译，再把产物复制到精简镜像 |
| `npm ci` | 比 npm install 更严格的依赖安装 |
| `nginx.conf` | 配置静态文件托管 + 反向代理 |
| `docker-compose.yml` | 编排多容器，定义服务、网络、卷 |
| `volumes` | 数据持久化，容器删除后数据仍在 |
| `healthcheck` | 检测服务是否就绪 |
| `depends_on` | 控制容器启动顺序 |
| `os.getenv()` | 读取环境变量，适配不同部署环境 |
| Vite proxy | 开发环境代理请求，避免 CORS |

---

## 七、项目结构（最终状态）

```
项目一/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # 入口 + lifespan
│   │   ├── database.py                # ★ 修改：环境变量连接
│   │   ├── models/student.py          # ORM 模型
│   │   ├── schemas/student.py         # Pydantic 模型
│   │   └── routers/students.py        # ★ 修改：搜索功能
│   ├── venv/
│   ├── requirements.txt
│   └── Dockerfile                     # ★ 新建
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue                    # ★ 修改：搜索+验证+删除确认
│   │   └── api/student.js             # ★ 修改：相对路径
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                 # ★ 修改：Vite 代理
│   ├── Dockerfile                     # ★ 新建
│   └── nginx.conf                     # ★ 新建
├── docs/
│   ├── day-1-notes.md
│   ├── day-2-notes.md
│   ├── day-3-notes.md
│   └── day-4-notes.md                 # ← 本文件
├── docker-compose.yml                 # ★ 新建
├── .gitignore
└── project-1-learning-plan.md
```

---

## 八、错误记录

| 错误 | 原因 | 解决 |
|------|------|------|
| 搜索后页面空白 | 忘传 keyword 参数到 API 函数 | `loadList()` 调用时传 `keyword.value` |
| `ElMessageBox.confirm` 没效果 | 没 `await` | 加 `await` 等待用户操作结果 |
| 表单验证不触发 | 忘记加 `prop="字段名"` | 每个 `el-form-item` 加 `prop` |
| Docker 构建失败 — `docker.1ms.run` 镜像找不到 | 国内镜像源没同步最新 tag | 换成 `docker.m.daocloud.io` |
| `docker-compose` 容器名空错误 | 项目目录名含特殊字符 | 加 `name: student-management` |
| Docker 端口 80 被占用 | 本机有服务占用了 80 | 改成 `8081:80` |
| 镜像源拉取失败 | 镜像源限流或不可用 | 替换可用镜像源 |

---

## 九、面试题

**Q：SQL LIKE 查询和 .contains() 的关系？**
A：`.contains()` 生成 `LIKE '%关键词%'`，前后模糊匹配。SQLAlchemy 还提供 `.startswith()`（`LIKE '关键词%'`）和 `.endswith()`。

**Q：删除操作为什么用 try/catch 包裹 ElMessageBox？**
A：用户点取消时，`ElMessageBox.confirm()` 会 reject Promise，不 catch 的话控制台报 Uncaught Promise 错误。

**Q：表单验证的 `trigger: 'blur'` 是什么？**
A：失焦时触发验证。还有 `trigger: 'change'`（值变化时触发），可根据用户体验选择。

**Q：Docker 多阶段构建解决了什么问题？**
A：最终镜像只包含运行时所需文件，不包含构建工具链（node、npm、编译器），大幅减小镜像体积。

**Q：docker-compose 中 `depends_on` 能保证服务就绪吗？**
A：默认只保证启动顺序，不保证服务已就绪。需要加 `condition: service_healthy` + `healthcheck` 才能真正等待。

**Q：Vite proxy 和 CORS 中间件有什么区别？**
A：Vite proxy 只在开发环境生效，让前端请求同源；CORS 中间件在生产环境也需要。生产环境用 Nginx 反代就不需要 CORS。

**Q：环境变量 `DATABASE_URL` 为什么在不同环境值不同？**
A：开发环境后端直接连本机 MySQL（`localhost:3308`），Docker 环境通过 compose 内部网络连接容器 MySQL（`mysql:3306`），主机名和端口都不同。

---

## 十、Day 4 练习题

### 选择题

| # | 题目 | 答案 |
|---|------|------|
| 1 | `Student.name.contains(keyword)` 生成什么 SQL？ | **B** `name LIKE '%keyword%'` |
| 2 | 搜索时为什么要重置 `page.value = 1`？ | **B** 避免翻到第3页后搜索无结果 |
| 3 | `ElMessageBox.confirm()` 用户点取消会发生什么？ | **B** Promise reject |
| 4 | `formRef.value.validate()` 的作用？ | **B** 触发表单所有字段验证 |
| 5 | `:rules` 绑定到哪个元素上？ | **B** `<el-form>` |
| 6 | Dockerfile 中 `RUN` 和 `CMD` 的区别？ | **B** `RUN` 构建时执行，`CMD` 启动时执行 |
| 7 | 多阶段构建的好处？ | **B** 最终镜像不包含构建工具链 |
| 8 | `healthcheck` 在 compose 中的作用？ | **B** 检测容器内服务是否已就绪 |
| 9 | Vite proxy 配置在哪个文件？ | **B** `vite.config.js` |
| 10 | `os.getenv("KEY", "default")` 的作用？ | **B** 读取环境变量，没有则用默认值 |

### 填空题

**1. 搜索接口参数**
```python
def list_students(page: int = 1, size: int = 10, ________: str = "", db: Session = Depends(get_db)):
    query = db.query(Student)
    if keyword:
        query = query.________(Student.name.________(keyword))
```
答案：`keyword`, `filter`, `contains`

**2. 删除确认**
```javascript
const handleDelete = async (id) => {
  try {
    await ________.________('确定要删除吗？', '警告', { type: 'warning' })
    await deleteStudent(id)
    loadList()
  } catch {
    // ________
  }
}
```
答案：`ElMessageBox`, `confirm`, 用户点了取消

**3. 表单验证**
```vue
<el-form ref="formRef" :model="form" :________="rules">
  <el-form-item label="姓名" ________="name" required>
    <el-input v-model="form.name" />
  </el-form-item>
</el-form>
```
```javascript
const rules = {
  name: [{ required: true, message: '请输入姓名', ________: 'blur' }],
  phone: [{ ________: /^1[3-9]\d{9}$/, message: '格式不正确', trigger: 'blur' }],
  email: [{ ________: 'email', message: '格式不正确', trigger: 'blur' }]
}
```
答案：`rules`, `prop`, `trigger`, `pattern`, `type`

### 简答题

**1. 用户点删除 → 弹出确认 → 点确定 → 删除成功，完整链路是怎样的？**

用户点"删除" → `handleDelete(id)` → `ElMessageBox.confirm()` 弹窗 → 用户点"确定" → Promise resolve → `deleteStudent(id)` → Axios DELETE 请求到 `DELETE /api/v1/students/{id}` → FastAPI 查数据库 → `db.delete()` + `db.commit()` → 返回 `{"message": "删除成功"}` → 前端收到响应 → `loadList()` 刷新表格。

**2. Docker compose 启动后通过什么地址访问？**

打开浏览器访问 `http://localhost:8081`：
- 首页 → Nginx 返回 `index.html`（前端页面）
- 点"新增"发 POST → Nginx 透传到 `http://backend:8000/api/v1/students/`
- 后端查数据库 → 返回 JSON → Nginx 返回给浏览器

**3. 开发环境和 Docker 生产环境有什么区别？**

开发模式是三个独立进程（Vite 5173 + Uvicorn 8001 + MySQL 3308），改代码热更新；Docker 是三个容器，访问 8081 走 Nginx，改代码要重新构建镜像。开发方便用前者，部署上线用后者。
