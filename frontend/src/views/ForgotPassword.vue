<template>
  <div class="forgot-password-container">
    <el-card class="forgot-password-card">
      <template #header>
        <div class="card-header">
          <h2>重置密码</h2>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="forgotPasswordForm">
        <el-form-item label="学　　号" prop="student_id">
          <el-input v-model="form.student_id" placeholder="请输入学号" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="姓　　名" prop="student_name">
          <el-input v-model="form.student_name" placeholder="请输入姓名" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="新　　码" prop="new_password">
          <el-input v-model="form.new_password" type="password" placeholder="请设置新密码" class="fixed-width-input"></el-input>
        </el-form-item>

        <el-form-item label="学生证照片" prop="student_card_photo">
          <el-upload
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleRemove"
            :limit="1"
            list-type="picture"
            ref="uploadRef">
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">请上传清晰的学生证正面照片用于身份验证（大小不超过7MB）</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading" style="width: 100%">
            提交重置申请
          </el-button>
        </el-form-item>

        <div class="forgot-password-links">
          <el-link type="primary" @click="$router.push('/')">返回登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 获取CSRF token的函数
const getCsrfToken = async () => {
  try {
    console.log('正在获取CSRF token...')
    const response = await axios.get('/api/users/csrf-token/')
    console.log('CSRF token获取成功:', response.data.csrfToken)
    return response.data.csrfToken
  } catch (error) {
    console.error('获取CSRF token失败:', error)
    ElMessage.error('获取安全令牌失败，请刷新页面重试')
    throw error
  }
}

const router = useRouter()
const forgotPasswordForm = ref()
const loading = ref(false)

const form = reactive({
  student_id: '',
  student_name: '',
  new_password: '',
  student_card_photo: null
})

const rules = reactive({
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  student_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }]
})

const handleFileChange = (file) => {
  form.student_card_photo = file.raw
}

const handleRemove = () => {
  form.student_card_photo = null
}

const handleSubmit = async () => {
  try {
    await forgotPasswordForm.value.validate()
    
    // 调试：检查文件状态
    console.log('学生证照片状态:', form.student_card_photo)
    console.log('文件类型:', typeof form.student_card_photo)
    console.log('是否为File对象:', form.student_card_photo instanceof File)
    
    loading.value = true

    // 先获取CSRF token，和注册接口保持一致
    const csrfToken = await getCsrfToken()
    
    const formData = new FormData()
    formData.append('student_id', form.student_id)
    formData.append('student_name', form.student_name)
    formData.append('new_password', form.new_password)
    formData.append('student_card_photo', form.student_card_photo)

    const response = await axios.post('/api/users/password-reset-request/', formData, {
      headers: {
        'X-CSRFToken': csrfToken
      }
    })
    if (response.data.success) {
      ElMessage.success(response.data.message)
      router.push('/')
    } else {
      ElMessage.error('提交失败，请重试')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.errors || '提交失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #DBD5E3;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.forgot-password-card {
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

.forgot-password-links {
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