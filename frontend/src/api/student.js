import axios from 'axios'

const api = axios.create({
    baseURL: '/api/v1'
})

// 加这3行 —— 请求拦截器
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

export const listStudents = (page, size,keyword) => api.get('/students/', { params: { page, size,keyword } })

export const getStudent = (id) => api.get(`/students/${id}`)

export const createStudent = (data) => api.post('/students/', data)

export const updateStudent = (id, data) => api.put(`/students/${id}`, data)

export const deleteStudent = (id) => api.delete(`/students/${id}`)

export const exportExcel = () => api.get('/students/export/excel', { responseType: 'blob' })
