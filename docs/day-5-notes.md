# Day 5：JWT 认证 + Excel 导出

> 全栈学生管理系统 ｜ 学习日期：2026-06-16

---

## 目录

- [一、Step 5 概述](#一step-5-概述)
- [二、JWT 认证后端](#二jwt-认证后端)
- [三、前端集成 JWT](#三前端集成-jwt)
- [四、Excel 导出](#四excel-导出)
- [五、完整知识点归纳](#五完整知识点归纳)
- [六、项目结构（最终状态）](#六项目结构最终状态)
- [七、错误记录](#七错误记录)
- [八、面试题](#八面试题)

---

## 一、Step 5 概述

### 做了什么

1. **JWT 后端** — 注册、登录、密码哈希、token 验证中间件
2. **前端登录页面** — 表单验证、调登录接口、存 token
3. **路由守卫** — 未登录自动跳转登录页
4. **axios 请求拦截器** — 每次请求自动带 Bearer token
5. **Excel 导出** — 后端生成 xlsx、前端下载文件

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/auth.py` | **新建** | JWT 配置、密码哈希、token 创建/验证 |
| `backend/app/models/user.py` | **新建** | User ORM 模型 |
| `backend/app/routers/auth.py` | **新建** | 注册 + 登录接口 |
| `backend/app/routers/students.py` | **修改** | 所有接口加 token 验证依赖 |
| `backend/app/routers/export.py` | **新建** | Excel 导出接口 |
| `backend/app/models/__init__.py` | **修改** | 导入 User 模型 |
| `backend/app/main.py` | **修改** | 注册 auth_router 和 export_router |
| `frontend/src/api/auth.js` | **新建** | 登录/注册 API |
| `frontend/src/api/student.js` | **修改** | 加请求拦截器、加 exportExcel 函数 |
| `frontend/src/views/LoginView.vue` | **新建** | 登录页面 |
| `frontend/src/views/StudentView.vue` | **修改** | 加导出按钮和 handleExport |
| `frontend/src/router/index.js` | **修改** | 加 /login 路由和导航守卫 |

---

## 二、JWT 认证后端

### 2.1 什么是 JWT

JWT（JSON Web Token）是一个三段式字符串，格式：`header.payload.signature`

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzgxMjY2MTQ2fQ.NHuJwjG7CcsU0UgIxgtPAtoc9EGigLtlaZM7C63y9mo
```

- **header** — 加密算法（HS256）
- **payload** — 用户 ID（sub）、过期时间（exp）等数据
- **signature** — 用密钥对 header+payload 签名，防止篡改

**登录后客户端的完整流程：**

```
用户输入账号密码
  → 后端验证通过
  → 生成 JWT（把用户 ID 放在 sub 字段，设置过期时间）
  → 返回给前端
  → 前端存到 localStorage
  → 后续请求在 Authorization header 带上
  → 后端解码 token 拿到用户 ID → 放行或拒绝
```

### 2.2 auth.py — JWT 工具函数

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "student-management-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """密码 -> 哈希（bcrypt 自动加盐）"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配存储的哈希"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise JWTError("token 中缺少 sub")
        return int(sub)
    except JWTError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")
```

**关键概念：**

| 概念 | 说明 |
|------|------|
| `SECRET_KEY` | 服务端密钥，用于签名和验证 token，泄露后任何人都能伪造 token |
| `ALGORITHM = "HS256"` | 对称加密算法，同一个密钥签名和验证 |
| `ACCESS_TOKEN_EXPIRE_MINUTES = 30` | token 30 分钟后过期 |
| `hash_password()` | bcrypt 加盐哈希，相同密码每次哈希结果不同 |
| `jwt.decode()` | 验证签名 + 检查过期时间，过期会抛 JWTError |
| `sub`（subject） | JWT 标准字段，这里存用户 ID |

### 2.3 注册接口

```python
@router.post("/register", status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    db_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "注册成功", "user_id": db_user.id}
```

- 先查用户名是否存在，不存在才创建
- `hash_password()` 明文→密文，不存明文密码
- `status_code=201` 表示资源创建成功

### 2.4 登录接口

```python
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

- `verify_password()` 比对明文和 bcrypt 哈希
- 登录成功才生成 token，失败一律 401（不告诉用户是用户名错还是密码错，防止暴力枚举）
- `sub` 字段存用户 ID（字符串）

### 2.5 在 students.py 中加 token 验证

```python
def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization 格式错误")
    token = authorization.split(" ")[1]
    return get_current_user_id(token)

@router.get("/students/")
def list_students(..., user_id: int = Depends(verify_token)):
    ...
```

- `Header(...)` — 从请求头取 `Authorization` 字段，不传就 422
- `Depends(verify_token)` — FastAPI 依赖注入，接口调用前先执行这个函数
- `Bearer ` + token — 标准的 Authorization 格式

---

## 三、前端集成 JWT

### 3.1 auth.js — 登录 API

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1/auth'
})

export const login = (data) => api.post('/login', data)
```

- 和 `student.js` 拆开成独立模块，按业务分离

### 3.2 LoginView.vue — 登录页面

```vue
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  // 1. 表单验证通过
  await formRef.value.validate()
  // 2. 调后端登录接口
  const res = await login(form)
  // 3. 存 token 到 localStorage
  localStorage.setItem('token', res.data.access_token)
  // 4. 跳转到首页
  ElMessage.success('登录成功')
  router.push('/')
}
</script>
```

**登录完整链路：**

```
用户输入 admin/123456 → 点登录
  → validate() 检查非空
  → POST /api/v1/auth/login { username, password }
  → 后端查 users 表 → verify_password → 生成 token
  → 返回 { access_token: "eyJ...", token_type: "bearer" }
  → 存入 localStorage
  → ElMessage.success('登录成功')
  → router.push('/') 跳首页
```

### 3.3 路由守卫

```javascript
// router/index.js
const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/', name: 'home', component: StudentView, meta: { requiresAuth: true } }
]

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')          // 没 token → 跳登录
  } else if (to.path === '/login' && token) {
    next('/')               // 已登录 → 跳过登录页
  } else {
    next()                  // 正常放行
  }
})
```

**导航守卫（Navigation Guard）执行顺序：**

```
用户访问 /
  → beforeEach 触发
  → 读取 localStorage 的 token
  → / 有 requiresAuth → 没有 token → next('/login')
  → 页面跳转 /login

用户登录后
  → 访问 /login → 发现已有 token → next('/') 跳过登录页
```

### 3.4 axios 请求拦截器

```javascript
// student.js
const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

**拦截器生命周期：**

```
点击"获取学生列表"
  → call listStudents()
  → axios 准备发 GET 请求
  → interceptors.request 执行（在请求发出前）
  → 从 localStorage 读 token → 塞进 headers.Authorization
  → 请求发出 "Authorization: Bearer eyJ..."
  → 后端 verify_token 解码成功 → 返回数据
```

---

## 四、Excel 导出

### 4.1 数据结构流转

```
数据库 → Student ORM 对象 → openpyxl Workbook → BytesIO 二进制流
  → StreamingResponse（HTTP 响应）
  → 前端收到 Blob → 创建下载链接 → 浏览器下载 students.xlsx
```

### 4.2 后端导出接口

```python
@router.get("/students/export/excel")
def export_students_excel(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    students = db.query(Student).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "学生列表"
    ws.append(["ID", "姓名", "年龄", "性别", "班级", "电话", "邮箱", "地址", "创建时间", "更新时间"])

    for s in students:
        ws.append([s.id, s.name, s.age, ...])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=students.xlsx"}
    )
```

| 关键类/函数 | 作用 |
|-------------|------|
| `Workbook()` | 创建新 Excel 工作簿 |
| `ws.append([])` | 按行写入数据 |
| `BytesIO()` | 内存二进制流，不写磁盘 |
| `wb.save(output)` | 把工作簿保存到内存流 |
| `output.seek(0)` | 重置流指针到开头（否则读不到内容） |
| `StreamingResponse` | FastAPI 流式返回文件 |
| `Content-Disposition: attachment` | 告诉浏览器弹出下载对话框 |
| `media_type` | Excel 文件的 MIME 类型 |

### 4.3 前端下载

```javascript
// student.js
export const exportExcel = () => api.get('/students/export/excel', { responseType: 'blob' })

// StudentView.vue
const handleExport = async () => {
  const res = await exportExcel()
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = 'students.xlsx'
  link.click()
  window.URL.revokeObjectURL(url)
}
```

**Blob 下载原理：**

```
后端返回二进制 Excel 流
  → axios 设置 responseType: 'blob'（不当作 JSON 解析）
  → window.URL.createObjectURL(new Blob([res.data]))
    在内存中创建一个临时的 URL（blob:http://...）
  → 创建 <a> 标签，设置 href=blobURL, download=文件名
  → link.click() 模拟点击 → 浏览器弹出下载
  → revokeObjectURL() 释放内存
```

| 概念 | 说明 |
|------|------|
| `responseType: 'blob'` | 告诉 axios 把响应体当做二进制数据，不转 JSON |
| `Blob` | 二进制大对象，可以表示任意文件 |
| `createObjectURL()` | 在浏览器内存中创建一个指向 Blob 的临时 URL |
| `revokeObjectURL()` | 释放该 URL，否则占用内存直到页面关闭 |

---

## 五、完整知识点归纳

### JWT 认证

| 概念 | 一句话解释 |
|------|-----------|
| JWT | 三段式 token（header.payload.signature），存用户身份和过期时间 |
| `SECRET_KEY` | 服务端密钥，token 签名和验签用 |
| bcrypt | 密码哈希算法，自动加盐，相同密码每次哈希结果不同 |
| `sub` | JWT 标准字段，存用户唯一标识 |
| `exp` | JWT 标准字段，存过期时间戳 |
| `Depends()` | FastAPI 依赖注入，在接口执行前运行一些代码 |
| `Header(...)` | 从 HTTP 请求头取参数，不传就报错 |
| `401 Unauthorized` | 认证失败的标准状态码 |

### 前端认证

| 概念 | 一句话解释 |
|------|-----------|
| `localStorage` | 浏览器本地存储，页面关闭不丢失 |
| 导航守卫 `beforeEach` | 路由跳转前执行，用于权限检查 |
| `meta.requiresAuth` | 路由元信息标记该页面需要登录 |
| `localStorage.getItem('token')` | 从本地存储取 token |
| 请求拦截器 | axios 发请求前自动执行，统一加 token |
| `interceptors.request.use()` | 注册请求拦截器回调 |

### Excel 导出

| 概念 | 一句话解释 |
|------|-----------|
| `Workbook` | openpyxl 的工作簿对象，对应一个 xlsx 文件 |
| `ws.append()` | 按行写入数据到工作表 |
| `BytesIO` | 内存中的二进制流，不写磁盘 |
| `StreamingResponse` | FastAPI 流式返回大文件 |
| `Content-Disposition` | HTTP 响应头，控制浏览器文件下载行为 |
| `responseType: 'blob'` | axios 配置，把响应当做二进制处理 |
| `Blob` | 浏览器中的二进制对象 |
| `URL.createObjectURL()` | 创建指向 Blob 的临时 URL 触发下载 |

---

## 六、项目结构（最终状态）

```
项目一/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                        # ★ 修改：注册 auth + export 路由
│   │   ├── database.py
│   │   ├── auth.py                        # ★ 新建：JWT + bcrypt
│   │   ├── models/
│   │   │   ├── __init__.py                # ★ 修改：导入 User
│   │   │   ├── student.py
│   │   │   └── user.py                    # ★ 新建：User ORM 模型
│   │   ├── schemas/student.py
│   │   └── routers/
│   │       ├── students.py                # ★ 修改：加 token 验证
│   │       ├── auth.py                    # ★ 新建：注册 + 登录
│   │       └── export.py                  # ★ 新建：Excel 导出
│   ├── venv/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/index.js                # ★ 修改：登录路由 + 导航守卫
│   │   ├── api/
│   │   │   ├── auth.js                    # ★ 新建：登录/注册 API
│   │   │   └── student.js                 # ★ 修改：请求拦截器 + exportExcel
│   │   ├── views/
│   │   │   ├── LoginView.vue              # ★ 新建：登录页面
│   │   │   └── StudentView.vue            # ★ 修改：加导出按钮
│   │   └── components/
│   │       ├── StudentTable.vue
│   │       └── StudentForm.vue
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
│   ├── day-1-notes.md
│   ├── day-2-notes.md
│   ├── day-3-notes.md
│   ├── day-4-notes.md
│   └── day-5-notes.md                     # ← 本文件
├── docker-compose.yml
├── .gitignore
└── project-1-learning-plan.md
```

---

## 七、错误记录

| 错误 | 原因 | 解决 |
|------|------|------|
| `v-model cannot be used on a prop` | Vue 3 禁止子组件直接 v-model 修改父组件的 prop | 用 `:model-value` + `@update:model-value="$emit('close')"` |
| 后端返回 500 登录时报错 | users 表可能还没创建或数据库连接失败 | 检查 MySQL 容器是否在运行 |
| `docker: command not found` | Docker 安装目录不在 PATH 环境变量中 | 把 `C:\Program Files\Docker\Docker\resources\bin` 加到系统环境变量 |

---

## 八、面试题

**Q：JWT 和 Session 有什么区别？**
A：Session 的会话数据存在服务端内存/Redis，客户端只存 session ID；JWT 的所有数据都在 token 本身。Session 需要存储空间，但可以主动失效；JWT 无状态、可跨服务，但签发后无法主动撤销。

**Q：为什么密码不能用明文存数据库？**
A：一旦数据库泄露，所有用户的密码直接暴露。bcrypt 加盐哈希后，即使数据库泄露攻击者也拿不到原始密码。

**Q：`Bearer` 是什么？**
A：Bearer 是 HTTP Authorization 的标准认证方案，意思是"持有此 token 的人即可通行"。

**Q：`Depends(verify_token)` 为什么能实现登录校验？**
A：FastAPI 在每个请求处理前先执行 `verify_token` 函数，函数返回的用户 ID 通过参数注入到接口函数。如果验证失败，直接抛 HTTPException 终止请求，不执行后续代码。

**Q：`StreamingResponse` 和普通 JSON 响应有什么区别？**
A：普通 JSON 响应直接返回 Python 对象（dict/list），FastAPI 自动序列化。StreamingResponse 返回一个迭代器/流，适合文件、大数据的场景。

**Q：`BytesIO` 的作用？为什么不用临时文件？**
A：`BytesIO` 在内存中读写，不写磁盘——速度更快、无磁盘 IO、用完即释放。如果用临时文件需要 `tempfile` 创建→写入→读取→发送→删除，步骤多且慢。

**Q：前端下载 Excel 为什么要用 `responseType: 'blob'`？**
A：axios 默认把响应当 JSON 解析（JSON.parse），Excel 二进制不是合法 JSON，解析会报错。`blob` 告诉 axios 直接保留原始二进制数据。

**Q：导航守卫的三个参数 `to`、`from`、`next` 分别是什么？**
A：`to` 目标路由对象，`from` 来源路由对象，`next()` 执行跳转。不调用 `next()` 页面会卡住不动。

**Q：`localStorage` 和 `sessionStorage` 有什么区别？**
A：`localStorage` 数据不会过期（除非手动删），`sessionStorage` 关闭浏览器标签页就清除。

---

## 九、Day 5 练习题

### 选择题

| # | 题目 | 答案 |
|---|------|------|
| 1 | JWT 的三段结构是什么？ | **B** header.payload.signature |
| 2 | bcrypt 的 `hash_password()` 相同输入为什么每次输出不同？ | **C** 自动加随机盐 |
| 3 | `jwt.decode()` 时 token 过期会怎样？ | **B** 抛 JWTError |
| 4 | `Depends()` 在 FastAPI 中的作用？ | **C** 在执行接口前运行依赖函数 |
| 5 | 路由守卫中 `next('/login')` 的作用？ | **B** 跳转到登录页面 |
| 6 | axios 请求拦截器在什么时候执行？ | **A** 请求发出前 |
| 7 | `responseType: 'blob'` 的作用？ | **B** 把响应当做二进制处理 |
| 8 | `BytesIO` 的作用？ | **B** 在内存中读写二进制数据 |
| 9 | `Content-Disposition: attachment` 的作用？ | **B** 让浏览器弹出下载对话框 |
| 10 | `localStorage` 的数据什么时候清除？ | **C** 除非手动删除，否则永远保留 |

### 填空题

**1. JWT token 验证**
```python
def get_current_user_id(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.____("sub"))
        return user_id
    except JWTError:
        raise ________(status_code=401, detail="token 无效或已过期")
```
答案：`get`, `HTTPException`

**2. 登录接口**
```python
@router.post("/login", response_model=____)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(____.____ == user.username).first()
    if not db_user or not ____(user.password, db_user.________):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token = ____(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```
答案：`Token`, `User`, `username`, `verify_password`, `hashed_password`, `create_access_token`

**3. 路由守卫**
```javascript
router.____((to, from, next) => {
  const token = localStorage.____('token')
  if (to.meta.__________ && !token) {
    next('____')
  } else if (to.path === '/login' && token) {
    next('____')
  } else {
    next()
  }
})
```
答案：`beforeEach`, `getItem`, `requiresAuth`, `/login`, `/`

**4. Excel 导出（后端）**
```python
@router.get("/students/export/excel")
def export_students_excel(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    students = db.query(____).____()

    wb = ____()
    ws = wb.active
    ws.____(["ID", "姓名", "年龄", ...])

    output = ____()
    wb.save(output)
    output.____(0)

    return ________(
        output,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=students.xlsx"}
    )
```
答案：`Student`, `all`, `Workbook`, `append`, `BytesIO`, `seek`, `StreamingResponse`

### 简答题

**1. 用户从输入 admin/123456 到看到学生列表的完整链路？**

用户输入账号密码点登录 → LoginView.vue 的 handleLogin() → axios POST /api/v1/auth/login → 后端查 users 表，verify_password 验证密码 → create_access_token 生成 JWT → 前端存 localStorage → router.push('/') → beforeEach 检查 token 有值 → 放行 → StudentView.vue 的 loadList() → axios GET /api/v1/students/ → 请求拦截器从 localStorage 取 token → 塞进 Authorization: Bearer xxx → 后端 verify_token 解码 → Depends 注入 user_id → 查 students 表 → 返回数据 → 前端渲染表格。

**2. Vue 3 中 prop 为什么不能直接 v-model？**

prop 是父组件向子组件传递数据的单向通道，子组件不允许修改 prop 的值。`v-model` 本质是 `:value="x"` + `@input="x = $event"` 的语法糖，后者会直接修改 prop——Vue 3 在运行前就通过编译检查禁止了。正确做法是 `:model-value="prop"` + `@update:model-value="$emit('event')"`，让父组件响应事件去改自己的数据。

**3. 为什么 Excel 导出要用 StreamingResponse 而不是直接返回 JSON？**

Excel 文件是二进制格式，不是 JSON 字符串。StreamingResponse 可以直接输出二进制流，并设置正确的 Content-Type（`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`）和 Content-Disposition（告诉浏览器以附件形式下载）。
