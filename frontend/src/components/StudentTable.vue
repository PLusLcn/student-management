<template>
  <div>
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
          <el-button type="primary" size="small" @click="$emit('edit', row)">编辑</el-button>
          <el-button type="danger" size="small" @click="$emit('delete', row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      layout="total, prev, next"
      :total="total"
      :page-size="size"
      @current-change="$emit('page-change', $event)"
      style="margin-top: 10px"
    />
  </div>
</template>

<script setup>
defineProps({
  studentList: Array,
  total: Number,
  size: Number
})

defineEmits(['edit', 'delete', 'page-change'])
</script>
