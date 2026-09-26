# 错误日志 — 全栈学生管理系统

> 记录项目中遇到的所有报错和解决方案

---

## 2026-06-02

### 1. Docker 端口 3306 被占用

- **场景**：执行 `docker run --name student-mysql ... -p 3306:3306` 启动 MySQL
- **原因**：宿主机 3306 端口已被其他程序占用
- **解决**：改用 `-p 3308:3306`，宿主机映射 3308，容器内部仍用 3306

### 2. Docker 容器名冲突

- **场景**：第一次 `docker run` 失败后重试
- **原因**：第一次 run 虽然失败但容器已创建，同名容器无法再次创建
- **解决**：`docker rm student-mysql` 删除旧容器后重试

### 3. bash: ~touch: command not found

- **场景**：在 Git Bash 中输入 `~touch .gitignore`
- **原因**：`~` 不能直接拼在命令前，Shell 将其解析为家目录路径的一部分
- **解决**：去掉 `~`，直接用 `touch .gitignore`

### 4. Pylance 无法解析导入 fastapi

- **场景**：VSCode 中打开 backend 代码，`from fastapi import FastAPI` 报红波浪线
- **原因**：VSCode 没选 venv 解释器，仍在使用全局 Python
- **解决**：`Ctrl+Shift+P` → Python: Select Interpreter → 选择 venv 路径

### 5. ModuleNotFoundError: No module named 'fastapi'

- **场景**：运行 `uvicorn app.main:app --reload` 时提示
- **原因**：`pip install -r requirements.txt` 时没有激活虚拟环境，包装到了全局
- **解决**：激活 venv 后重新 `pip install -r requirements.txt`

### 6. Docker MySQL 端口映射重复

- **场景**：运行 `docker run -p 3308:3306` 时报端口绑定错误
- **原因**：前一节课的 MySQL 容器还在运行，占着 3308 端口
- **解决**：用 `docker ps` 查看后先 `docker stop student-mysql`，再 `docker rm student-mysql`，或直接 `docker rm -f student-mysql`

---

## 2026-06-03

### 7. Element Plus 组件无法解析（页面空白）

- **场景**：启动前端后发现页面空白，控制台报 `el-button` 无法解析
- **原因**：`main.js` 中 `app.use(ElementPlus)` 写在了 `app.mount('#app')` 之后，插件注册没生效
- **解决**：先 `app.use(ElementPlus)` 再 `app.mount('#app')`

### 8. CORS 拦截：No 'Access-Control-Allow-Origin'

- **场景**：前端发请求到后端被浏览器拦截
- **原因**：旧 uvicorn 进程成僵尸占着端口，新进程实际没跑起来，前端访问的是死进程
- **解决**：在 PowerShell 用 `Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process` 杀进程，再重新启动 uvicorn

### 9. 列表接口返回 500

- **场景**：前端访问学生列表，网络面板状态 500
- **原因**：`response_model=dict` 不能序列化 SQLAlchemy ORM 对象，缺少 `model_validate()` 转换
- **解决**：在 `list_students` 返回前用 `StudentResponse.model_validate(s)` 将 ORM 对象转为 Pydantic 模型

### 10. 编辑弹窗下拉框报错

- **场景**：点击编辑，弹窗中性别下拉框报未处理错误
- **原因**：`el-select` 的 `v-model` 绑定值在编辑回填时类型不匹配或默认值缺失
- **解决**：确保 `form.value` 重置时 `gender` 有默认值 `'男'`

---

## 2026-06-04

### 11. 搜索后页面空白

- **场景**：输入关键字点搜索，表格空白
- **原因**：`loadList()` 调用 `listStudents(page, size, keyword)` 时没传 `keyword.value`
- **解决**：`loadList` 内部改成 `listStudents(page.value, size.value, keyword.value)`

### 12. ElMessageBox.confirm 没效果

- **场景**：点删除按钮没弹出确认框，直接删除了
- **原因**：没加 `await`，代码不等待用户操作直接往下执行删除
- **解决**：`await ElMessageBox.confirm(...)`

### 13. 表单验证不触发

- **场景**：空表单点提交，没有提示错误
- **原因**：`el-form-item` 忘记加 `prop="字段名"`
- **解决**：每个需要验证的表单项加上 `prop`，值与 rules 中的 key 对应

### 14. Docker 构建失败 — 镜像源找不到

- **场景**：`docker-compose build` 时拉取 `python:3.13-slim` 等镜像失败
- **原因**：国内镜像源 `docker.1ms.run`、`docker.xuanyuan.me` 没有同步最新的镜像 tag 或被限流
- **解决**：将 `daemon.json` 中的镜像源换为 `https://docker.m.daocloud.io`

### 15. docker-compose 容器名空错误

- **场景**：`docker-compose up` 时报容器名相关的错误
- **原因**：项目目录名包含特殊字符（中文或空格），docker-compose 自动生成的项目名有问题
- **解决**：在 `docker-compose.yml` 顶部加 `name: student-management` 显式指定项目名

### 16. Docker 端口 80 被占用

- **场景**：`docker-compose up` 时 Nginx 绑定 80 端口失败
- **原因**：本机某个服务（PID 6116）占用了 80 端口
- **解决**：compose 中前端端口改为 `8081:80`，访问 `http://localhost:8081`

### 17. Docker 镜像拉取 short read / unexpected EOF

- **场景**：DaoCloud 镜像源拉取 `nginx:alpine` 和 `node:24-alpine` 时失败
- **原因**：国内网络不稳定，镜像源返回了不完整的数据
- **解决**：重试多次或更换可用镜像源，最终因网络问题未完成 compose 测试

---

## 使用说明

- 每次遇到报错立即记录，复制完整报错信息
- 解决方案要落实到具体操作（命令/代码行）
- 同一个错误反复出现时在原因分析里补充"根源"
