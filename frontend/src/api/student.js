import axios from 'axios'

const api = axios.create({
    baseURL: '/api/v1'
})

export const listStudents = (page, size,keyword) => api.get('/students/', { params: { page, size,keyword } })

export const getStudent = (id) => api.get(`/students/${id}`)

export const createStudent = (data) => api.post('/students/', data)

export const updateStudent = (id, data) => api.put(`/students/${id}`, data)

export const deleteStudent = (id) => api.delete(`/students/${id}`)
