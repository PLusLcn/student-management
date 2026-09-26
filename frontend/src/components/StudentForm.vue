<template>
  <el-dialog :model-value="visible" @update:model-value="$emit('close')" :title="isEdit ? '编辑学生' : '新增学生'" width="500px">

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
      <el-form-item label="电话" prop="phone">
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
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  isEdit: Boolean,
  form: Object,
  rules: Object
})

const emit = defineEmits(['close', 'save'])
const formRef = ref(null)

const handleCancel = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    emit('save')
  } catch {
    // 校验不通过
  }
}
</script>
