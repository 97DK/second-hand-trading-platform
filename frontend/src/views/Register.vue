<!-- frontend/src/views/Register.vue -->
<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>学生注册</h2>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="registerForm">
        <el-form-item label="学　　号" prop="student_id">
          <el-input v-model="form.student_id" placeholder="请输入学号" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="用户名　" prop="username">
          <el-input v-model="form.username" placeholder="请设置用户名" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="密　　码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请设置密码" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="学生证照片" prop="student_card_photo">
          <el-upload
            action="/api/users/register/"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleRemove"
            :limit="1"
            list-type="picture"
            ref="uploadRef">
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">请上传清晰的学生证正面照片（大小不超过7MB）</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">
            注册
          </el-button>
        </el-form-item>

        <div class="register-links">
          <el-link type="primary" @click="$router.push('/')">返回登录</el-link>
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
const registerForm = ref()
const loading = ref(false)
const uploadRef = ref()

const form = reactive({
  student_id: '',
  username: '',
  password: '',
  confirmPassword: '',
  student_card_photo: null
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive({
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  student_card_photo: [{ required: true, message: '请上传学生证照片', trigger: 'change' }]
})

const handleFileChange = (file) => {
  form.student_card_photo = file.raw
}

const handleRemove = () => {
  form.student_card_photo = null
}

const handleRegister = async () => {
  try {
    await registerForm.value.validate()
    loading.value = true

    const formData = new FormData()
    formData.append('student_id', form.student_id)
    formData.append('username', form.username)
    formData.append('password', form.password)
    formData.append('confirm_password', form.confirmPassword)
    // 学生证照片是必填项
    if (form.student_card_photo) {
      formData.append('student_card_photo', form.student_card_photo)
    }
    // 如果没有上传照片，就不传递这个字段，让后端返回明确的错误提示

    const result = await authStore.register(formData)
    console.log('Register result:', result)
    if (result.success) {
      ElMessage.success(result.message)
      router.push('/waiting')
    } else {
      console.log('Registration failed with message:', result.message)
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Register error:', error)
    ElMessage.error('注册过程中出现错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #DBD5E3;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.register-card {
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

.register-links {
  display: flex;
  justify-content: center;
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

/* 左对齐标签 */
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