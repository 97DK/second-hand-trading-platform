<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>登录</h2>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="loginForm">
        <el-form-item label="登录身份" prop="user_type">
          <el-radio-group v-model="form.user_type">
            <el-radio label="student">学生</el-radio>
            <el-radio label="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入学号/用户名" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="密　码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>

        <div class="login-links">
          <el-link type="primary" @click="$router.push('/register')">学生注册</el-link>
          <el-link type="info" @click="$router.push('/forgot-password')">忘记密码</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loginForm = ref()
const loading = ref(false)

const form = reactive({
  user_type: 'student',
  username: '',
  password: ''
})

const rules = reactive({
  user_type: [{ required: true, message: '请选择登录身份', trigger: 'change' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

const handleLogin = async () => {
  try {
    await loginForm.value.validate()
    loading.value = true

    // 确保获取CSRF token
    const result = await authStore.login(form)
    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error('登录过程中发生错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #DBD5E3;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.login-card {
  width: 400px;
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.5); /* 50% 透明度 */
  border-radius: 10px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  color: #737BBE;
}

.fixed-width-input {
  width: 300px;
}

.login-links {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

/* 自定义Element Plus主色调 */
:deep(.el-button--primary) {
  background-color: #737BBE;
  border-color: #737BBE;
}

:deep(.el-button--primary:hover) {
  background-color: #6269a9;
  border-color: #6269a9;
}

:deep(.el-button--primary:focus) {
  background-color: #737BBE;
  border-color: #737BBE;
}

:deep(.el-link.el-link--primary) {
  color: #737BBE;
}

:deep(.el-link.el-link--primary:hover) {
  color: #6269a9;
}

/* 修改单选按钮的颜色 */
:deep(.el-radio__input.is-checked .el-radio__inner) {
  border-color: #737BBE;
  background-color: #737BBE;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #737BBE;
}

:deep(.el-radio__inner:hover) {
  border-color: #737BBE;
}

/* 去除标签宽度固定以实现左对齐 */
:deep(.el-form-item__label) {
  text-align: left !important;
  padding-right: 12px !important;
  width: auto !important;
}

/* 左对齐表单内容 */
:deep(.el-form-item__content) {
  display: flex;
  justify-content: flex-start;
}

/* 去除自动填充的蓝色背景 */
:deep(.el-input__inner:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0px 1000px white inset !important;
  -webkit-text-fill-color: #333 !important;
}

:deep(.el-input__inner:-webkit-autofill:focus) {
  -webkit-box-shadow: 0 0 0px 1000px white inset !important;
}
</style>