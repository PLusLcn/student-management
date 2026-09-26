# 数据库设计

> 数据库：MySQL 8.0
> 字符集：utf8mb4
> ORM 框架：SQLAlchemy

---

## 数据库信息

| 项 | 值 |
|------|------|
| 数据库名 | student_db |
| 用户名 | root |
| 密码 | root123 |
| 端口 | 3308（宿主机）→ 3306（容器） |
| 字符集 | utf8mb4 |

---

## 学生表（students）

### DDL

```sql
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

### 字段说明

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 唯一主键 |
| name | VARCHAR(50) | NOT NULL | 学生姓名 |
| age | INT | NOT NULL | 年龄 |
| gender | ENUM('男','女','其他') | DEFAULT '其他' | 性别 |
| grade | VARCHAR(20) | NOT NULL | 班级 |
| phone | VARCHAR(20) | 可选 | 手机号 |
| email | VARCHAR(100) | 可选 | 邮箱 |
| address | VARCHAR(200) | 可选 | 住址 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 自动记录创建时间 |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | 自动记录更新时间 |

### 设计理由

| 字段 | 为什么加 |
|------|---------|
| id | 每张表都需要唯一主键 |
| name | 学生基本标识，也是搜索字段 |
| age | 最常见的查询条件之一 |
| gender | 用 ENUM 限制可选值，减少脏数据 |
| grade | 按班级管理是常见需求 |
| phone/email | 联系信息，可选字段示范 |
| address | 选填字段，展示可选字段处理方式 |
| created_at / updated_at | 每张表都要有，排序和追踪用 |
