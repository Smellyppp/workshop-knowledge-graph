/**
 * 认证状态管理
 * 管理用户登录状态、令牌和用户信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  // 状态定义
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 计算属性：是否已登录
  const isAuthenticated = computed(() => !!token.value)
  // 计算属性：是否为管理员
  const isAdmin = computed(() => user.value?.user_type === 1)

  /**
   * 用户登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise<boolean>} 登录是否成功
   */
  async function login(username, password) {
    try {
      const response = await axios.post('/api/v1/auth/login', {
        username,
        password
      })

      // 保存令牌和用户信息
      token.value = response.data.access_token
      user.value = response.data.user

      // 持久化到本地存储
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '登录失败')
      return false
    }
  }

  /**
   * 用户登出
   */
  async function logout() {
    try {
      // 调用登出接口
      await axios.post('/api/v1/auth/logout')
    } catch (error) {
      console.error('登出错误:', error)
    } finally {
      // 清除本地状态和存储
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('登出成功')
    }
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser() {
    try {
      const response = await axios.get('/api/v1/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('获取用户信息错误:', error)
      logout()
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchCurrentUser
  }
})
