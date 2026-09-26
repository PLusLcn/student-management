# API 接口规范

> 基础 URL：`http://localhost:8000`
> 数据格式：JSON

---

## 学生管理（5 个接口）

### 1. 获取学生列表

```
GET /students/?page=1&size=10&keyword=
```

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| size | int | 10 | 每页条数 |
| keyword | str | "" | 按姓名模糊搜索 |

**响应 200：**

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
      "created_at": "2026-06-02T10:00:00",
      "updated_at": "2026-06-02T10:00:00"
    }
  ],
  "total": 1
}
```

---

### 2. 获取单个学生

```
GET /students/{id}
```

**响应 200：** 单个学生对象（同上）
**响应 404：** `{ "detail": "学生不存在" }`

---

### 3. 新增学生

```
POST /students/
```

**请求体：**

```json
{
  "name": "张三",
  "age": 20,
  "gender": "男",
  "grade": "计算机1班"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | str | ✅ | 姓名 |
| age | int | ✅ | 年龄 |
| gender | str | ✅ | 男/女/其他 |
| grade | str | ✅ | 班级 |
| phone | str | ❌ | 手机号 |
| email | str | ❌ | 邮箱 |
| address | str | ❌ | 住址 |

**响应 201：** 返回创建的学生对象

---

### 4. 更新学生

```
PUT /students/{id}
```

请求体同新增。响应 200 返回更新后对象。

---

### 5. 删除学生

```
DELETE /students/{id}
```

**响应 200：** `{ "message": "删除成功" }`

---

## 通用规范

| 规则 | 说明 |
|------|------|
| HTTP 方法 | GET 查 / POST 增 / PUT 改 / DELETE 删 |
| 状态码 | 200 成功 / 201 创建成功 / 404 不存在 / 422 参数错误 |
| 错误格式 | 统一 `{ "detail": "错误信息" }` |
