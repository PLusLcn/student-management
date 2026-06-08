# Day 3：Vue3 前端页面 — Element Plus + Axios

> 全栈学生管理系统 ｜ 学习日期：2026-06-03

---

## 目录

- [一、Step 3 概述](#一step-3-概述)
- [二、CORS 跨域](#二cors-跨域)
- [三、Vite + Vue3 项目搭建](#三vite--vue3-项目搭建)
- [四、Element Plus 组件库](#四element-plus-组件库)
- [五、Axios 封装 API](#五axios-封装-api)
- [六、App.vue 页面结构](#六appvue-页面结构)
- [七、完整知识点归纳](#七完整知识点归纳)
- [八、项目结构（当前状态）](#八项目结构当前状态)
- [九、调试记录](#九调试记录)
- [十、下一步预告](#十下一步预告)

---

## 一、Step 3 概述

### 做了什么

用 Vue3 + Element Plus + Axios 写了一个完整的前端页面，跟后端 5 个 API 对接，实现增删改查全流程。

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/main.py` | **修改** | 加 CORS 中间件 |
| `frontend/` | **新建** | Vite 创建 Vue3 项目 |
| `frontend/src/main.js` | **修改** | 注册 Element Plus |
| `frontend/src/api/student.js` | **新建** | Axios 封装 5 个 API |
| `frontend/src/App.vue` | **修改** | 完整页面：表格+弹窗+表单 |

---

## 二、CORS 跨域

### 为什么需要 CORS

浏览器安全策略：前端 `http://localhost:5173` 请求后端 `http://localhost:8001`，**端口不同**就属于"跨域"，浏览器会拦截响应。

### 后端配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 关键概念

- **跨域**：协议、域名、端口任何一个不同，浏览器就认为是跨域
- **预检请求（OPTIONS）**：浏览器发 POST/PUT/DELETE 之前，先发一个 OPTIONS 请求问服务器"你允许这个域访问吗？"
- **`add_middleware`**：在每个响应上加 `Access-Control-Allow-Origin` 头，告诉浏览器"允许"

---

## 三、Vite + Vue3 项目搭建

### 创建命令

```bash
rm -rf frontend && npm create vite@latest frontend -- --template vue
cd frontend
npm install
```

### 目录结构

```
frontend/
├── index.html              # HTML 入口
├── package.json            # 依赖管理
├── vite.config.js          # Vite 配置
└── src/
    ├── main.js             # 入口：创建 Vue 实例，注册插件
    ├── App.vue             # 根组件
    ├── api/
    │   └── student.js      # ★ 新建：API 调用封装
    ├── components/
    └── assets/
```

---

## 四、Element Plus 组件库

### 安装

```bash
npm install element-plus
```

### 在 main.js 注册

```javascript
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
```

`app.use(ElementPlus)` 之后，页面里就能直接用 `<el-button>`、`<el-table>`、`<el-dialog>` 等组件。

### 用了哪些组件

| 组件 | 作用 | 关键属性 |
|------|------|---------|
| `<el-table>` | 数据表格 | `:data` 传数组 |
| `<el-table-column>` | 列定义 | `prop` 字段名，`label` 表头 |
| `<el-pagination>` | 分页 | `:total` 总数，`@current-change` 翻页 |
| `<el-dialog>` | 弹窗 | `v-model` 控制显隐 |
| `<el-form>` | 表单 | `:model` 绑定数据 |
| `<el-input>` | 输入框 | `v-model` 双向绑定 |
| `<el-select>` | 下拉选择 | `v-model` 绑定值 |
| `<el-button>` | 按钮 | `@click` 点击事件 |

---

## 五、Axios 封装 API

### 安装

```bash
npm install axios
```

### student.js

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8001/api/v1'
})

export const listStudents = (page, size) => api.get('/students/', { params: { page, size } })
export const getStudent = (id) => api.get(`/students/${id}`)
export const createStudent = (data) => api.post('/students/', data)
export const updateStudent = (id, data) => api.put(`/students/${id}`, data)
export const deleteStudent = (id) => api.delete(`/students/${id}`)
```

### 每个函数的作用

| 函数 | HTTP | 路径 | 说明 |
|------|------|------|------|
| `listStudents(page, size)` | GET | `/students/?page=1&size=10` | 分页列表 |
| `getStudent(id)` | GET | `/students/1` | 单个详情 |
| `createStudent(data)` | POST | `/students/` | 新增 |
| `updateStudent(id, data)` | PUT | `/students/1` | 更新 |
| `deleteStudent(id)` | DELETE | `/students/1` | 删除 |

### 为什么不直接用 fetch

- Axios 自动序列化 JSON
- Axios 自动处理错误
- 配置 `baseURL` 后不用每个接口写完整地址
- 语法简洁，代码量少

---

## 六、App.vue 页面结构

### 整体布局

```
┌─────────────────────────────────┐
│  学生管理系统          [新增学生] │
├────┬────┬──┬────┬────┬────┬────┤
│ ID │姓名│年龄│性别│班级│电话│操作│
├────┼────┼──┼────┼────┼────┼────┤
│  1 │张三│18│男  │一班│... │编辑│删除│
├────┼────┼──┼────┼────┼────┼────┤
│  2 │李四│19│女  │二班│... │编辑│删除│
└────┴────┴──┴────┴────┴────┴────┘
共 10 条          < 1  2  3 >
```

### 三个核心 Vue 概念

| 概念 | 写法 | 解释 |
|------|------|------|
| **响应式变量** | `const x = ref(0)` | 变量变了，页面自动刷新 |
| **双向绑定** | `v-model="form.name"` | 输入框的内容 ↔ 变量，自动同步 |
| **事件绑定** | `@click="handleAdd"` | 用户操作触发函数 |
| **动态属性** | `:data="studentList"` | 等号右边是 JS 表达式，不是字符串 |
| **计算属性** | `:title="isEdit ? '编辑' : '新增'"` | 根据条件动态显示不同内容 |

### 数据流

```
用户点击"新增" → handleAdd() → 清空表单 → 打开弹窗
用户填完点"确定" → submitForm() → axios.post() → 后端 → 数据库
                    → 关弹窗 → loadList() → 刷新表格
```

### 生命周期

`onMounted(loadList)` — 页面加载完成后自动获取学生列表。相当于网页版的"启动时运行"。

---

## 七、完整知识点归纳

### Vue3 核心

| 概念 | 一句话解释 |
|------|-----------|
| **`ref()`** | 把一个变量变成"响应式"的，改了值页面自动刷新 |
| **`.value`** | `ref` 包裹的变量取值用 `.value`，但模板里不需要 |
| **`v-model`** | 表单输入和变量之间的自动同步 |
| **`@click`** | `v-on:click` 的简写，绑定点击事件 |
| **`onMounted()`** | 组件加载完后执行，适合做初始化 |
| **`<template>`** | .vue 文件的模板部分，写 HTML |
| **`<script setup>`** | .vue 文件的逻辑部分，写 JS |

### Element Plus 核心

- 标签都是 `<el-xxx>` 格式
- `:data` 传数组，`prop` 映射字段
- `v-model` 控制弹窗显隐和表单数据
- 不需要自己写 CSS 样式

### Axios 核心

- `axios.create({ baseURL })` 设置通用前缀
- `.get()`、`.post()` 等方法对应 HTTP 方法
- 返回 Promise，用 `async/await` 接收数据
- 自动 JSON 序列化/反序列化

### CORS 核心

- 不同端口算跨域
- 后端加 `CORSMiddleware` 解决
- `allow_origins` 只允许指定域名访问
- 浏览器发"复杂请求"前先发 OPTIONS 预检

---

## 八、项目结构（当前状态）

```
项目一/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # ★ 修改：加 CORS 中间件
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── student.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── student.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── students.py            # ★ 修改：修复 ORM 序列化
│   ├── venv/
│   └── requirements.txt
├── frontend/                           # ★ 新增：Vue3 前端项目
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js                     # ★ 修改：注册 Element Plus
│       ├── App.vue                     # ★ 修改：完整增删改查页面
│       └── api/
│           └── student.js              # ★ 新增：API 封装
├── docs/
│   ├── day-1-notes.md
│   ├── day-2-notes.md
│   └── day-3-notes.md
├── .gitignore
└── project-1-learning-plan.md
```

---

## 九、调试记录

| 错误 | 原因 | 解决 |
|------|------|------|
| 页面空白，报 `el-button` 无法解析 | `main.js` 里 `app.use(ElementPlus)` 写在了 `mount()` 之后，没生效 | 先 `app.use()` 再 `mount()` |
| CORS 拦截：No 'Access-Control-Allow-Origin' | 旧 uvicorn 进程成僵尸，占着端口不释放，新进程实际没跑起来 | 换端口或用 PowerShell 杀僵尸进程 |
| 列表接口返回 500 | `response_model=dict` 不能序列化 ORM 对象 | 用 `StudentResponse.model_validate()` 手动转换 |
| 编辑时下拉框触发了未处理错误 | `el-select` 的 `v-model` 绑定值在编辑回填时类型匹配问题 | 确保表单重置时 `gender` 有默认值 |

---

## 十一、课后测验

### 第 1 题（单选）
前端在 `localhost:5173`，后端在 `localhost:8001`，浏览器报跨域错误。为什么？
- A. 域名不同
- **B. 端口不同** ✓
- C. 协议不同
- D. 浏览器版本太旧

> 域名都是 localhost，协议都是 HTTP，只有端口不同。端口不同就算跨域。

### 第 2 题（填空）
后端解决 CORS 需要在 FastAPI 里加 `app.**add_middleware**(CORSMiddleware, ...)`，并在 `allow_origins` 里写上前端地址。

### 第 3 题（判断）
`const name = ref('张三')`，在 `<template>` 里要用 `name.value` 才能拿到值。
**错** ✓

> 模板里 Vue 自动解包 `.value`，直接写 `{{ name }}` 就行。`.value` 只在 `<script>` 里需要用。

### 第 4 题（单选）
`v-model="form.name"` 的作用是：
- A. 给表单设置标题
- **B. 把输入框的内容和 `form.name` 双向绑定** ✓
- C. 校验输入框是否必填
- D. 提交表单到后端

### 第 5 题（单选）
想让页面加载完自动调用 `loadList()`，应该写在：
- **A. `onMounted(loadList)`** ✓
- B. `onCreated(loadList)`
- C. `watch(loadList)`
- D. 直接在 `<script setup>` 顶层写 `loadList()`

> `onMounted` 是 Vue 的生命周期钩子，组件渲染完成后执行。写在顶层虽然能执行，但组件还没渲染完就可能出问题。

### 第 6 题（多选）
下面哪些说法是对的？
- **A. `<el-table :data="list">` 中的 `:data` 前面的冒号表示右边是 JS 表达式** ✓
- **B. `<el-pagination>` 的 `@current-change` 在切换页码时触发** ✓
- **C. `ref()` 包裹的变量变了，页面会自动重新渲染** ✓
- **D. `axios.create({ baseURL })` 可以避免每个请求都写完整地址** ✓

> ABCD 全对。C 是 Vue 最核心的特性——响应式。

### 第 7 题（填空）
App.vue 里的数据流顺序是：
用户点"新增" → **`handleAdd()`** → 弹窗出现 → 填完点确定 → **`submitForm()`** → 后端写数据库 → 返回 → 关弹窗 → **`loadList()`** → 表格刷新

### 第 8 题（代码纠错）
```javascript
const app = createApp(App)
app.mount('#app')        // ❌ 错在位置
app.use(ElementPlus)
```
> 要先注册插件再挂载。改正：
> ```javascript
> const app = createApp(App)
> app.use(ElementPlus)     // 先注册插件
> app.mount('#app')        // 再挂载到 DOM
> ```

### 第 9 题（简答）
从 Axios 发请求到后端返回数据，完整链路：
1. Axios 把 JS 对象自动序列化成 JSON
2. Axios 发 HTTP 请求到 FastAPI
3. FastAPI 收到请求，校验参数类型（query 参数 / body 参数）
4. 调用对应的路由函数（如 `list_students`）
5. 函数通过 SQLAlchemy 操作 MySQL 数据库
6. 返回 ORM 对象 → Pydantic 序列化成 JSON
7. FastAPI 返回 HTTP 响应给前端
8. Axios 解析 JSON 成 JS 对象
9. Vue 把数据赋值给 `ref()` 变量 → 页面自动刷新

### 第 10 题（实操）— 搜索学生功能
**功能描述**：输入姓名关键字，点搜索按钮，表格只显示匹配的学生。

**前端改动（3 个文件）**：
| 文件 | 改动 |
|------|------|
| `api/student.js` | 加 `listStudents(page, size, keyword)`，params 加 `keyword` |
| `App.vue` | 加 `<el-input>` 输入框和搜索按钮，`:model` 绑定 `keyword`；点搜索时调 `loadList(1, keyword)` |
| `App.vue` | `loadList` 函数接收 `keyword` 参数并传给 API |

**后端改动（1 个文件）**：
| 文件 | 改动 |
|------|------|
| `routers/students.py` | `list_students` 函数加参数 `keyword: str = ""`，查询时加 `.filter(Student.name.contains(keyword))` |

> 核心思路：**前端多传一个参数到后端 → 后端 SQL 查询加一个 WHERE 条件**。SQLAlchemy 的 `.contains()` 对应 MySQL 的 `LIKE '%关键字%'`。

---

## 十二、下一步预告

**Step 4：优化与部署准备**。包括：
- 前后端表单校验（必填字段、手机号格式等）
- 删除前确认弹窗
- 搜索/筛选功能
- 打包前端，用 FastAPI 托管静态文件
- 统一部署方案
