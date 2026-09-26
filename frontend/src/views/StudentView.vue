<script setup>
import { ref, onMounted } from 'vue'
import { listStudents, createStudent, updateStudent, deleteStudent } from '../api/student'
import { ElMessageBox } from 'element-plus'
import StudentTable from '../components/StudentTable.vue'
import StudentForm from '../components/StudentForm.vue'
import { exportExcel } from '../api/student'

const studentList = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const keyword = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({
  name: '', age: 18, gender: '男', grade: '',
  phone: '', email: '', address: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入班级', trigger: 'blur' }],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }]
}

const loadList = async () => {
  const res = await listStudents(page.value, size.value, keyword.value)
  studentList.value = res.data.items
  total.value = res.data.total
}

const handlePageChange = (p) => {
  page.value = p
  loadList()
}

const search = () => {
  page.value = 1
  loadList()
}
// 新增学生
const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  form.value = { name: '', age: 18, gender: '男', grade: '', phone: '', email: '', address: '' }
  dialogVisible.value = true
}
// 编辑学生
const handleEdit = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}
// 保存学生
const handleSave = async () => {
  if (isEdit.value) {
    await updateStudent(editId.value, form.value)
  } else {
    await createStudent(form.value)
  }
  dialogVisible.value = false
  loadList()
}
// 删除学生
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
    // 用户点了取消
  }
}
// 导出 Excel
const handleExport = async () => {
  const res = await exportExcel()
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.download = 'students.xlsx'
  link.click()
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  loadList()
})
</script>

<template>
  <div style="padding: 20px">
    <h1>学生管理系统</h1>
    <el-button type="primary" @click="handleAdd" style="margin-bottom: 10px">新增学生</el-button>
    <el-button type="success" @click="handleExport" style="margin-bottom: 10px">导出 Excel</el-button>
    <div style="margin-bottom: 10px; display: flex; gap: 10px">
      <el-input v-model="keyword" placeholder="搜索姓名" style="width: 200px" clearable />
      <el-button type="primary" @click="search">搜索</el-button>
    </div>

    <StudentTable
      :student-list="studentList"
      :total="total"
      :size="size"
      @edit="handleEdit"
      @delete="handleDelete"
      @page-change="handlePageChange"
    />

    <StudentForm
      :visible="dialogVisible"
      :is-edit="isEdit"
      :form="form"
      :rules="rules"
      @close="dialogVisible = false"
      @save="handleSave"
    />
  </div>
</template>
