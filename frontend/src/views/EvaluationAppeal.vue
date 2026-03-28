<template>
  <div class="evaluation-appeal">
    <el-page-header @back="goBack" :content="'商品评价申诉'" />
    
    <div class="appeal-container" v-if="evaluation">
      <!-- 评价详情 -->
      <el-card class="evaluation-card">
        <template #header>
          <div class="card-header">
            <span>评价详情</span>
          </div>
        </template>
        
        <div class="evaluation-info">
          <h3>{{ evaluation.product_title }}</h3>
          <div class="evaluation-details">
            <p><strong>买家：</strong>{{ evaluation.buyer_nickname }}</p>
            <p><strong>评价时间：</strong>{{ formatDate(evaluation.created_at) }}</p>
            <p><strong>申诉状态：</strong>
              <el-tag :type="getStatusTagType(evaluation.appeal_status)">
                {{ evaluation.appeal_status_display }}
              </el-tag>
            </p>
            <p v-if="evaluation.appeal_deadline"><strong>申诉截止时间：</strong>{{ formatDate(evaluation.appeal_deadline) }}</p>
          </div>
          
          <!-- 评价内容 -->
          <div class="evaluation-content">
            <h4>评价内容：</h4>
            <ul>
              <li>是否收到货：{{ evaluation.received_item === 'yes' ? '是' : '否' }}</li>
              <li>是否与商品描述一致：{{ evaluation.description_match === 'yes' ? '是' : '否' }}</li>
              <li>商家服务态度：{{ evaluation.service_attitude === 'yes' ? '是' : '否' }}</li>
            </ul>
          </div>
          
          <!-- 证据照片 -->
          <div v-if="evaluation.evidence_photos && evaluation.evidence_photos.length > 0" class="evidence-photos">
            <h4>证据照片：</h4>
            <div class="photo-grid">
              <el-image
                v-for="(photo, index) in evaluation.evidence_photos"
                :key="index"
                :src="photo.url"
                :preview-src-list="evaluation.evidence_photos.map(p => p.url)"
                class="evidence-photo"
                fit="cover"
              />
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 申诉表单 -->
      <el-card class="appeal-form-card" v-if="canAppeal">
        <template #header>
          <div class="card-header">
            <span>提交申诉</span>
          </div>
        </template>
        
        <el-form :model="appealForm" :rules="appealRules" ref="appealFormRef" label-width="100px">
          <el-form-item label="申诉理由" prop="appeal_content">
            <el-input
              v-model="appealForm.appeal_content"
              type="textarea"
              :rows="6"
              placeholder="请详细说明您认为评价不合理的具体原因..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="申诉证据">
            <el-upload
              v-model:file-list="appealEvidencePhotos"
              list-type="picture-card"
              :auto-upload="false"
              :limit="5"
              :on-change="handleAppealPhotoChange"
              :on-remove="handleAppealPhotoRemove"
            >
              <el-icon><Plus /></el-icon>
              <template #file="{ file }">
                <div>
                  <img class="el-upload-list__item-thumbnail" :src="file.url" alt="" />
                  <span class="el-upload-list__item-actions">
                    <span
                      class="el-upload-list__item-preview"
                      @click="handlePictureCardPreview(file)"
                    >
                      <el-icon><zoom-in /></el-icon>
                    </span>
                    <span
                      v-if="!disabled"
                      class="el-upload-list__item-delete"
                      @click="handleAppealPhotoRemove(file)"
                    >
                      <el-icon><Delete /></el-icon>
                    </span>
                  </span>
                </div>
              </template>
            </el-upload>
            <div class="el-upload__tip">
              最多可上传5张证据照片，支持jpg/png格式
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="submitAppeal" 
              :loading="submitting"
              size="large"
            >
              提交申诉
            </el-button>
            <el-button @click="goBack" size="large">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 申诉结果展示 -->
      <el-card class="appeal-result-card" v-if="evaluation.appeal_status !== 'pending'">
        <template #header>
          <div class="card-header">
            <span>申诉处理结果</span>
          </div>
        </template>
        
        <div class="appeal-result">
          <p><strong>申诉内容：</strong>{{ evaluation.appeal_content }}</p>
          <p><strong>处理结果：</strong>{{ evaluation.appeal_response }}</p>
          <p><strong>处理时间：</strong>{{ formatDate(evaluation.updated_at) }}</p>
        </div>
      </el-card>
    </div>
    
    <el-empty v-else description="加载中..." />
    
    <!-- 图片预览对话框 -->
    <el-dialog v-model="dialogVisible" title="图片预览">
      <img w-full :src="dialogImageUrl" alt="Preview Image" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const evaluation = ref(null)
const submitting = ref(false)
const appealFormRef = ref()
const appealEvidencePhotos = ref([])
const dialogImageUrl = ref('')
const dialogVisible = ref(false)
const disabled = ref(false)

// 申诉表单
const appealForm = ref({
  appeal_content: ''
})

// 表单验证规则
const appealRules = {
  appeal_content: [
    { required: true, message: '请输入申诉理由', trigger: 'blur' },
    { min: 10, message: '申诉理由至少需要10个字', trigger: 'blur' }
  ]
}

// 计算属性：判断是否可以申诉
const canAppeal = computed(() => {
  if (!evaluation.value) return false
  return evaluation.value.appeal_status === 'pending' && 
         new Date() < new Date(evaluation.value.appeal_deadline)
})

// 获取状态标签类型
const getStatusTagType = (status) => {
  const statusMap = {
    'pending': 'info',
    'submitted': 'warning',
    'resolved': 'success'
  }
  return statusMap[status] || 'info'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 处理申诉证据照片变化
const handleAppealPhotoChange = (file, fileList) => {
  // 将文件转换为base64格式存储
  const reader = new FileReader()
  reader.onload = (e) => {
    appealEvidencePhotos.value = fileList.map(item => ({
      name: item.name,
      url: e.target.result
    }))
  }
  reader.readAsDataURL(file.raw)
}

// 处理申诉证据照片移除
const handleAppealPhotoRemove = (file, fileList) => {
  appealEvidencePhotos.value = fileList
}

// 图片预览
const handlePictureCardPreview = (file) => {
  dialogImageUrl.value = file.url
  dialogVisible.value = true
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取评价详情
const fetchEvaluationDetail = async () => {
  try {
    const response = await axios.get(`/api/products/appeal/${route.params.id}/`)
    evaluation.value = response.data
  } catch (error) {
    if (error.response?.status === 404) {
      ElMessage.error('评价不存在或您无权限查看')
      router.back()
    } else {
      ElMessage.error('获取评价详情失败')
    }
  }
}

// 提交申诉
const submitAppeal = async () => {
  if (!await appealFormRef.value?.validate()) return
  
  submitting.value = true
  try {
    const requestData = {
      appeal_content: appealForm.value.appeal_content
    }
    
    // 如果有申诉证据照片，添加到请求数据中
    if (appealEvidencePhotos.value.length > 0) {
      requestData.appeal_evidence_photos = appealEvidencePhotos.value
    }
    
    const response = await axios.post(`/api/products/appeal/${route.params.id}/`, requestData)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 更新评价信息
      evaluation.value = response.data.data
      // 重置表单
      appealForm.value.appeal_content = ''
      appealEvidencePhotos.value = []
    }
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('提交申诉失败')
    }
  } finally {
    submitting.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchEvaluationDetail()
})
</script>

<style scoped>
.evaluation-appeal {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.appeal-container {
  margin-top: 20px;
}

.evaluation-card, .appeal-form-card, .appeal-result-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.evaluation-info h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.evaluation-details {
  margin-bottom: 20px;
}

.evaluation-details p {
  margin: 5px 0;
  color: #606266;
}

.evaluation-content h4 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.evaluation-content ul {
  margin: 0;
  padding-left: 20px;
}

.evaluation-content li {
  margin: 5px 0;
  color: #606266;
}

.evidence-photos h4 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}

.evidence-photo {
  width: 120px;
  height: 120px;
  border-radius: 4px;
  overflow: hidden;
}

.appeal-result {
  line-height: 1.6;
}

.appeal-result p {
  margin: 10px 0;
  color: #606266;
}

.appeal-result strong {
  color: #303133;
}

/* 申诉证据上传样式 */
.el-upload--picture-card {
  width: 120px;
  height: 120px;
  line-height: 120px;
}

.el-upload-list--picture-card .el-upload-list__item {
  width: 120px;
  height: 120px;
}

.el-upload__tip {
  margin-top: 10px;
  color: #909399;
  font-size: 12px;
}
</style>