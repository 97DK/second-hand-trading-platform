<template>
  <div class="admin-appeal-management">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">商家申诉管理</span>
      </template>
    </el-page-header>
    
    <el-card class="appeals-card">
      <template #header>
        <div class="card-header">
          <span>待处理申诉列表</span>
          <el-badge :value="pendingAppeals.length" type="warning" />
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton animated>
          <template #template>
            <el-skeleton-item variant="p" style="width: 30%" />
            <div style="margin-top: 20px">
              <el-skeleton-item variant="text" style="width: 60%" />
            </div>
          </template>
        </el-skeleton>
      </div>
      
      <div v-else-if="pendingAppeals.length === 0" class="empty-container">
        <el-empty description="暂无待处理的申诉">
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </el-empty>
      </div>
      
      <div v-else class="appeals-list">
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item 
            v-for="appeal in pendingAppeals" 
            :key="appeal.id"
            :name="appeal.id"
          >
            <template #title>
              <div class="appeal-header">
                <div class="header-info">
                  <h3>{{ appeal.product_title }}</h3>
                  <p class="appeal-info">
                    卖家：{{ appeal.seller_nickname }} 
                    <el-tag size="small" type="info" style="margin-left: 10px;">{{ formatDate(appeal.created_at) }}</el-tag>
                  </p>
                </div>
                <div class="status-tags">
                  <el-tag type="warning" effect="dark">待审核</el-tag>
                </div>
              </div>
            </template>
            
            <div class="appeal-details">
              <!-- 买家评价内容 -->
              <div class="evaluation-section">
                <h4>买家评价内容：</h4>
                <ul class="evaluation-items">
                  <li :class="{ 'negative-item': appeal.received_item === 'no' }">
                    是否收到货：{{ appeal.received_item === 'yes' ? '是' : '否' }}
                  </li>
                  <li :class="{ 'negative-item': appeal.description_match === 'no' }">
                    是否与商品描述一致：{{ appeal.description_match === 'yes' ? '是' : '否' }}
                  </li>
                  <li :class="{ 'negative-item': appeal.service_attitude === 'no' }">
                    商家服务态度：{{ appeal.service_attitude === 'yes' ? '是' : '否' }}
                  </li>
                </ul>
                
                <!-- 预计扣分 -->
                <div class="deduction-preview" v-if="calculateDeductionPoints(appeal) > 0">
                  <h4>预计扣分：</h4>
                  <el-tag type="danger" size="large">
                    -{{ calculateDeductionPoints(appeal) }} 分
                  </el-tag>
                </div>
              </div>
              
              <!-- 买家证据照片 -->
              <div v-if="appeal.evidence_photos && appeal.evidence_photos.length > 0" class="evidence-section">
                <h4>买家证据照片：</h4>
                <div class="photo-grid">
                  <el-image
                    v-for="(photo, index) in appeal.evidence_photos"
                    :key="index"
                    :src="photo.url"
                    :preview-src-list="appeal.evidence_photos.map(p => p.url)"
                    class="evidence-photo"
                    fit="cover"
                    lazy
                  />
                </div>
              </div>
              
              <!-- 卖家申诉内容 -->
              <div class="appeal-content">
                <h4>卖家申诉内容：</h4>
                <p class="appeal-text">{{ appeal.appeal_content }}</p>
              </div>
              
              <!-- 卖家申诉证据 -->
              <div v-if="appeal.appeal_evidence_photos && appeal.appeal_evidence_photos.length > 0" class="appeal-evidence-section">
                <h4>卖家申诉证据：</h4>
                <div class="photo-grid">
                  <el-image
                    v-for="(photo, index) in appeal.appeal_evidence_photos"
                    :key="index"
                    :src="photo.url"
                    :preview-src-list="appeal.appeal_evidence_photos.map(p => p.url)"
                    class="evidence-photo"
                    fit="cover"
                    lazy
                  />
                </div>
              </div>
              
              <!-- 管理员操作 -->
              <div class="admin-actions">
                <h4>管理员操作：</h4>
                <div class="action-buttons">
                  <el-button 
                    type="success" 
                    @click="handleAppeal(appeal.id, 'approve')"
                    :loading="processing"
                  >
                    申诉通过（不扣分）
                  </el-button>
                  <el-button 
                    type="danger" 
                    @click="showRejectDialog(appeal)"
                    :loading="processing"
                  >
                    申诉驳回（正常扣分）
                  </el-button>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
    
    <!-- 驳回原因对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="填写驳回原因" width="500px">
      <el-form :model="rejectForm" :rules="rejectRules" ref="rejectFormRef">
        <el-form-item label="驳回原因" prop="response_content">
          <el-input
            v-model="rejectForm.response_content"
            type="textarea"
            :rows="4"
            placeholder="请输入驳回的具体原因..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rejectDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmReject" :loading="processing">确定驳回</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const pendingAppeals = ref([])
const loading = ref(true)
const processing = ref(false)
const activeNames = ref([])
const rejectDialogVisible = ref(false)
const currentAppeal = ref(null)

// 驳回表单
const rejectForm = ref({
  response_content: ''
})
const rejectFormRef = ref()

const rejectRules = {
  response_content: [
    { required: true, message: '请输入驳回原因', trigger: 'blur' },
    { min: 5, message: '驳回原因至少需要5个字', trigger: 'blur' }
  ]
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 刷新数据
const refreshData = () => {
  fetchPendingAppeals()
}

// 获取待处理申诉列表
const fetchPendingAppeals = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/products/admin/appeals/')
    pendingAppeals.value = response.data
  } catch (error) {
    ElMessage.error('获取申诉列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 计算扣分点数
const calculateDeductionPoints = (appeal) => {
  let deduction = 0
  if (appeal.received_item === 'no') deduction += 10
  if (appeal.description_match === 'no') deduction += 5
  if (appeal.service_attitude === 'no') deduction += 2
  return deduction
}

// 处理申诉（通过或驳回）
const handleAppeal = async (appealId, action) => {
  try {
    await ElMessageBox.confirm(
      action === 'approve' 
        ? '确定要通过此申诉吗？通过后将不扣除卖家信用分。' 
        : '确定要驳回此申诉吗？驳回后将正常扣除卖家信用分。',
      action === 'approve' ? '申诉通过确认' : '申诉驳回确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: action === 'approve' ? 'success' : 'warning'
      }
    )
    
    processing.value = true
    const response = await axios.post('/api/products/admin/appeals/', {
      evaluation_id: appealId,
      action: action,
      response_content: action === 'approve' ? '申诉通过，维持原评价' : '申诉驳回，评价有效'
    })
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      // 移除已处理的申诉
      pendingAppeals.value = pendingAppeals.value.filter(appeal => appeal.id !== appealId)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('处理申诉失败')
      console.error(error)
    }
  } finally {
    processing.value = false
  }
}

// 显示驳回对话框
const showRejectDialog = (appeal) => {
  currentAppeal.value = appeal
  rejectForm.value.response_content = ''
  rejectDialogVisible.value = true
}

// 确认驳回
const confirmReject = async () => {
  if (!await rejectFormRef.value?.validate()) return
  
  try {
    processing.value = true
    const response = await axios.post('/api/products/admin/appeals/', {
      evaluation_id: currentAppeal.value.id,
      action: 'reject',
      response_content: rejectForm.value.response_content
    })
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
      rejectDialogVisible.value = false
      // 移除已处理的申诉
      pendingAppeals.value = pendingAppeals.value.filter(appeal => appeal.id !== currentAppeal.value.id)
      currentAppeal.value = null
    }
  } catch (error) {
    ElMessage.error('驳回申诉失败')
    console.error(error)
  } finally {
    processing.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchPendingAppeals()
})
</script>

<style scoped>
.admin-appeal-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.appeals-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  padding: 40px 20px;
}

.empty-container {
  padding: 60px 20px;
  text-align: center;
}

.appeal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-info h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.appeal-info {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.status-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.appeal-details {
  padding: 20px 0;
}

.evaluation-section h4,
.evidence-section h4,
.appeal-content h4,
.appeal-evidence-section h4,
.admin-actions h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.evaluation-items {
  list-style: none;
  padding: 0;
  margin: 0 0 20px 0;
}

.evaluation-items li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.evaluation-items li:last-child {
  border-bottom: none;
}

.negative-item {
  color: #f56c6c;
  font-weight: bold;
}

.deduction-preview {
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 6px;
  padding: 15px;
  margin: 20px 0;
}

.deduction-preview h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.evidence-photo {
  width: 100%;
  height: 120px;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s;
}

.evidence-photo:hover {
  transform: scale(1.05);
}

.appeal-text {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
  margin: 0 0 20px 0;
  line-height: 1.6;
  color: #606266;
}

.admin-actions {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.action-buttons {
  display: flex;
  gap: 15px;
}

@media (max-width: 768px) {
  .admin-appeal-management {
    padding: 10px;
  }
  
  .appeal-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .photo-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>