/**
 * 路由配置文件
 * 定义应用的所有路由及其访问权限
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由配置列表
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }  // 登录页不需要认证
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },  // 需要认证
    redirect: '/users',             // 默认重定向到用户列表页
    children: [
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { requiresAuth: true }  // 需要认证
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/Chat.vue'),
        meta: { requiresAuth: true }  // 需要认证
      }
    ]
  },
  {
    // 404 重定向
    path: '/:pathMatch(.*)*',
    redirect: '/users'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：路由访问控制
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 需要认证但未登录，跳转到登录页
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  }
  // 已登录用户访问登录页，跳转到用户列表页
  else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/users')
  }
  // 其他情况正常放行
  else {
    next()
  }
})

export default router
