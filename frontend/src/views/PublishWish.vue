<!-- frontend/src/views/PublishWish.vue -->
<template>
  <div class="publish-wish">
    <el-card>
      <template #header>
        <h2 class="publish-wish-title">发布心愿</h2>
      </template>

      <el-form
        :model="wishForm"
        :rules="rules"
        ref="wishFormRef"
        label-width="100px"
      >
        <!-- 标题 -->
        <el-form-item label="心愿标题" prop="title">
          <el-input
            v-model="wishForm.title"
            placeholder="请输入心愿标题，例如：想要一本高等数学教材"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- 描述 -->
        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="wishForm.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述你想要的商品，包括品牌、型号、规格、颜色等要求"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <!-- 最高预算 -->
        <el-form-item label="最高预算" prop="max_price">
          <el-input
            v-model.number="wishForm.max_price"
            placeholder="请输入你能接受的最高价格"
            type="number"
            min="0"
            max="999999"
            step="0.01"
          >
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button
            class="publish-wish-button"
            @click="submitWish"
            :loading="loading"
            size="large"
          >
            发布心愿
          </el-button>
          <el-button @click="resetForm" size="large">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()

// 表单引用
const wishFormRef = ref()

// 响应式数据
const loading = ref(false)

// 心愿表单数据
const wishForm = reactive({
  title: '',
  description: '',
  max_price: null
})

// 验证规则
const rules = {
  title: [
    { required: true, message: '请输入心愿标题', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入详细描述', trigger: 'blur' }
  ],
  max_price: [
    { type: 'number', min: 0, message: '价格必须大于等于0', trigger: 'blur' }
  ]
}

// 重置表单
const resetForm = () => {
  wishFormRef.value.resetFields()
}

// 提交心愿
const submitWish = async () => {
  try {
    await wishFormRef.value.validate()
    loading.value = true

    // 提交到后端
    const response = await axios.post('/api/products/wishes/', wishForm)

    if (response.data.id) {
      ElMessage.success('心愿发布成功，等待管理员审核')
      router.push('/wishlist')
    } else {
      throw new Error('发布失败')
    }
  } catch (error) {
    ElMessage.error('心愿发布失败，请检查填写内容')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish-wish {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.publish-wish-title {
  color: #737BBE;
  text-align: center;
  margin: 0;
}

.el-input {
  width: 100%;
}

:deep(.el-form-item__label) {
  color: #737BBE;
}

:deep(.el-form-item__content) {
  color: #737BBE;
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  color: #737BBE;
}

.publish-wish-button {
  background-color: #737BBE;
  border-color: #737BBE;
  color: white;
}

.publish-wish-button:hover {
  background-color: #6269a9;
  border-color: #6269a9;
  color: white;
}

.publish-wish-button:focus {
  background-color: #737BBE;
  border-color: #737BBE;
  color: white;
}
</style>