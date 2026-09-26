import axios from 'axios'

const api = axios.create({
    baseURL: '/api/v1/auth'
})

export const login = (data) => api.post('/login', data)
export const register = (data) => api.post('/register', data)
