import { createRouter, createWebHistory } from 'vue-router'
import StudentView from '../views/StudentView.vue'
import LoginView from '../views/LoginView.vue'

const routes = [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/', name: 'home', component: StudentView, meta: { requiresAuth: true } }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 导航守卫：没 token 就跳登录页
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/')
    } else {
        next()
    }
})

export default router
