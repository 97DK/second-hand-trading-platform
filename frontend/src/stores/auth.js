import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

// 配置axios
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  // 获取CSRF token
  const getCsrfToken = async () => {
    try {
      const response = await axios.get('/api/users/csrf-token/')
      return response.data.csrfToken
    } catch (error) {
      console.error('Failed to get CSRF token:', error)
      throw error
    }
  }

  const login = async (loginData) => {
    try {
      // 确保有CSRF token
      await getCsrfToken()

      const response = await axios.post('/api/users/login/', loginData)
      if (response.data.success) {
        user.value = response.data.user
        isAuthenticated.value = true
        return { success: true }
      } else {
        return {
          success: false,
          message: response.data.message || '登录失败'
        }
      }
    } catch (error) {
      console.error('Login API error:', error)
      
      // 特别处理400状态码（业务逻辑错误）
      if (error.response?.status === 400) {
        return {
          success: false,
          message: error.response.data?.message || '登录失败'
        }
      }
      
      // 处理403 CSRF错误
      if (error.response?.status === 403) {
        return {
          success: false,
          message: 'CSRF验证失败，请刷新页面重试'
        }
      }
      
      // 其他网络错误
      return {
        success: false,
        message: error.response?.data?.message || '登录过程中发生错误'
      }
    }
  }

  const register = async (registerData) => {
    try {
      // 确保有CSRF token
      await getCsrfToken()

      const response = await axios.post('/api/users/register/', registerData)
      console.log('Register API response:', response.data)
      if (response.data.success) {
        return response.data
      } else {
        return {
          success: false,
          message: response.data.message || '注册失败'
        }
      }
    } catch (error) {
      console.error('Register API error:', error)
      console.log('Error response:', error.response?.data)
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data?.errors || '注册失败'
      }
    }
  }

  const logout = async () => {
    try {
      await axios.post('/api/users/logout/')
    } catch (error) {
      console.error('Logout API error:', error)
    } finally {
      // Always clear local state regardless of API success
      user.value = null
      isAuthenticated.value = false

      // Clear CSRF token cookie
      document.cookie = "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/"
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout
  }
})


