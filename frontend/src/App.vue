<script setup>
import { ref, onMounted } from 'vue'
import { listStudents, createStudent, updateStudent, deleteStudent } from './api/student'
import { ElMessageBox } from 'element-plus'


const studentList = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({
  name: '', age: 18, gender: '男', grade: '',
  phone: '', email: '', address: ''
})

// 加载列表
const loadList = async () => {
  const res = await listStudents(page.value, size.value,keyword.value)
  studentList.value = res.data.items
  total.value = res.data.total
}

// 翻页
const handlePageChange = (p) => {
  page.value = p
  loadList()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  form.value = { name: '', age: 18, gender: '男', grade: '', phone: '', email: '', address: '' }
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

// 提交
const formRef = ref(null)

const submitForm = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await updateStudent(editId.value, form.value)
    } else {
      await createStudent(form.value)
    }
    dialogVisible.value = false
    loadList()
  } catch {
    // 校验不通过，什么都不做 
  }
  
}

// 删除
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该学生吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteStudent(id)
    loadList()
  } catch {
    // 用户点了取消，什么都不做
  }
}


// 搜索
const keyword = ref('')

const search = () => {
  page.value = 1
  loadList()
}

// 校验规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入班级', trigger: 'blur' }],
  phone: [{
    pattern: /^1[3-9]\d{9}$/,
    message: '手机号格式不正确',
    trigger: 'blur'
  }],
  email: [{
    type: 'email',
    message: '邮箱格式不正确',
    trigger: 'blur'
  }]
}


// 页面加载后自动获取数据
onMounted(() => {
  loadList()
})
</script>

<template>
  <div style="padding: 20px">
    <h1>学生管理系统</h1>
    <el-button type="primary" @click="handleAdd" style="margin-bottom: 10px">新增学生</el-button>
    <!-- 搜索框 -->
    <div style="margin-bottom: 10px; display: flex; gap: 10px">
      <el-input v-model="keyword" placeholder="搜索姓名" style="width: 200px" clearable />
      <el-button type="primary" @click="search">搜索</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="studentList" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="age" label="年龄" width="80" />
      <el-table-column prop="gender" label="性别" width="80" />
      <el-table-column prop="grade" label="班级" width="120" />
      <el-table-column prop="phone" label="电话" width="150" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column label="操作" min-width="200">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      layout="total, prev, next"
      :total="total"
      :page-size="size"
      @current-change="handlePageChange"
      style="margin-top: 10px"
    />

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学生' : '新增学生'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="姓名" prop="name" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="年龄" prop="age" required>
          <el-input-number v-model="form.age" :min="1" :max="200" />
        </el-form-item>
        <el-form-item label="性别" prop="gender" required>
          <el-select v-model="form.gender">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" prop="grade" required>
          <el-input v-model="form.grade" />
        </el-form-item>
        <el-form-item label="电话" prop="phone" >
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
