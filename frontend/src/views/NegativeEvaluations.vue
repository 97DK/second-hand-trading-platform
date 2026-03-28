<!-- frontend/src/views/NegativeEvaluations.vue -->
<template>
  <div class="negative-evaluations">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">负面评价管理</span>
      </template>
    </el-page-header>
    
    <el-card class="evaluations-card">
      <template #header>
        <div class="card-header">
          <span>收到的负面评价</span>
          <el-badge :value="evaluations.length" type="danger" />
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
      
      <div v-else-if="evaluations.length === 0" class="empty-container">
        <el-empty description="暂无负面评价">
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </el-empty>
      </div>
      
      <div v-else class="evaluations-list">
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item 
            v-for="evaluation in evaluations" 
            :key="evaluation.id"
            :name="evaluation.id"
          >
            <template #title>
              <div class="evaluation-header">
                <div class="header-info">
                  <h3>{{ evaluation.product.title }}</h3>
                  <p class="buyer-info">
                    买家：{{ evaluation.buyer_nickname }} 
                    <el-tag size="small" type="info">{{ formatDate(evaluation.created_at) }}</el-tag>
                  </p>
                </div>
                <div class="status-tags">
                  <el-tag 
                    v-if="evaluation.appeal_status === 'pending' && new Date() < new Date(evaluation.appeal_deadline)"
                    type="warning"
                    effect="dark"
                  >
                    待申诉
                  </el-tag>
                  <el-tag 
                    v-else-if="evaluation.appeal_status === 'submitted'"
                    type="primary"
                    effect="dark"
                  >
                    申诉中
                  </el-tag>
                  <el-tag 
                    v-else-if="evaluation.appeal_status === 'resolved'"
                    type="success"
                    effect="dark"
                  >
                    已处理
                  </el-tag>
                  <el-tag 
                    v-else
                    type="danger"
                    effect="dark"
                  >
                    申诉超时
                  </el-tag>
                  
                  <el-tag 
                    v-if="isNegative(evaluation)" 
                    type="danger" 
                    size="small"
                    style="margin-left: 10px;"
                  >
                    负面评价
                  </el-tag>
                </div>
              </div>
            </template>
            
            <div class="evaluation-details">
              <!-- 评价内容 -->
              <div class="evaluation-content">
                <h4>评价详情：</h4>
                <ul class="evaluation-items">
                  <li :class="{ 'negative-item': evaluation.received_item === 'no' }">
                    是否收到货：{{ evaluation.received_item === 'yes' ? '是' : '否' }}
                    <span v-if="evaluation.received_item === 'no'" class="reason-tag">未收到货物</span>
                  </li>
                  <li :class="{ 'negative-item': evaluation.description_match === 'no' }">
                    是否与商品描述一致：{{ evaluation.description_match === 'yes' ? '是' : '否' }}
                    <span v-if="evaluation.description_match === 'no'" class="reason-tag">描述不符</span>
                  </li>
                  <li :class="{ 'negative-item': evaluation.service_attitude === 'no' }">
                    商家服务态度：{{ evaluation.service_attitude === 'yes' ? '是' : '否' }}
                    <span v-if="evaluation.service_attitude === 'no'" class="reason-tag">服务态度差</span>
                  </li>
                </ul>
                
                <!-- 扣分预览 -->
                <div class="deduction-preview" v-if="calculateDeductionPoints(evaluation) > 0">
                  <h4>预计扣分：</h4>
                  <el-tag type="danger" size="large">
                    -{{ calculateDeductionPoints(evaluation) }} 分
                  </el-tag>
                  <div class="deduction-reasons">
                    <span 
                      v-for="reason in getDeductionReasons(evaluation)" 
                      :key="reason"
                      class="reason-chip"
                    >
                      {{ getReasonLabel(reason) }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- 证据照片 -->
              <div v-if="evaluation.evidence_photos && evaluation.evidence_photos.length > 0" class="evidence-section">
                <h4>证据照片：</h4>
                <div class="photo-grid">
                  <el-image
                    v-for="(photo, index) in evaluation.evidence_photos"
                    :key="index"
                    :src="photo.url"
                    :preview-src-list="evaluation.evidence_photos.map(p => p.url)"
                    class="evidence-photo"
                    fit="cover"
                    lazy
                  />
                </div>
              </div>
              
              <!-- 申诉截止时间 -->
              <div v-if="evaluation.appeal_deadline" class="deadline-section">
                <h4>申诉信息：</h4>
                <p>
                  申诉截止时间：{{ formatDateTime(evaluation.appeal_deadline) }}
                  <span 
                    :class="getTimeStatusClass(evaluation)"
                    style="margin-left: 10px;"
                  >
                    {{ getTimeStatus(evaluation) }}
                  </span>
                </p>
                <p v-if="evaluation.appeal_response" class="appeal-response">
                  处理结果：{{ evaluation.appeal_response }}
                </p>
              </div>
              
              <!-- 操作按钮 -->
              <div class="action-buttons">
                <el-button 
                  v-if="canAppeal(evaluation)"
                  type="warning" 
                  @click="goToAppeal(evaluation.id)"
                >
                  立即申诉
                </el-button>
                <el-button 
                  type="primary" 
                  @click="viewProduct(evaluation.product.id)"
                >
                  查看商品
                </el-button>
                <el-button 
                  type="info" 
                  @click="contactBuyer(evaluation.buyer.id)"
                >
                  联系买家
                </el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const evaluations = ref([])
const loading = ref(true)
const activeNames = ref([])

// 返回上一页
const goBack = () => {
  router.back()
}

// 刷新数据
const refreshData = () => {
  fetchNegativeEvaluations()
}

// 获取负面评价列表
const fetchNegativeEvaluations = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/products/negative-evaluations/')
    evaluations.value = response.data
  } catch (error) {
    ElMessage.error('获取负面评价失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 判断是否为负面评价
const isNegative = (evaluation) => {
  return evaluation.received_item === 'no' || 
         evaluation.description_match === 'no' || 
         evaluation.service_attitude === 'no'
}

// 计算扣分点数
const calculateDeductionPoints = (evaluation) => {
  let deduction = 0
  if (evaluation.received_item === 'no') deduction += 10
  if (evaluation.description_match === 'no') deduction += 5
  if (evaluation.service_attitude === 'no') deduction += 2
  return deduction
}

// 获取扣分原因
const getDeductionReasons = (evaluation) => {
  const reasons = []
  if (evaluation.received_item === 'no') reasons.push('not_received')
  if (evaluation.description_match === 'no') reasons.push('description_mismatch')
  if (evaluation.service_attitude === 'no') reasons.push('poor_service')
  return reasons
}

// 获取原因标签
const getReasonLabel = (reason) => {
  const labels = {
    'not_received': '未收到货物(-10分)',
    'description_mismatch': '描述不符(-5分)',
    'poor_service': '服务态度差(-2分)'
  }
  return labels[reason] || reason
}

// 判断是否可以申诉
const canAppeal = (evaluation) => {
  return evaluation.appeal_status === 'pending' && 
         new Date() < new Date(evaluation.appeal_deadline)
}

// 获取时间状态
const getTimeStatus = (evaluation) => {
  if (evaluation.appeal_status === 'resolved') {
    return '已处理'
  }
  
  const now = new Date()
  const deadline = new Date(evaluation.appeal_deadline)
  
  if (now > deadline) {
    return '已超时'
  }
  
  const diffHours = Math.floor((deadline - now) / (1000 * 60 * 60))
  if (diffHours > 0) {
    return `剩余${diffHours}小时`
  }
  
  const diffMinutes = Math.floor((deadline - now) / (1000 * 60))
  return `剩余${diffMinutes}分钟`
}

// 获取时间状态样式类
const getTimeStatusClass = (evaluation) => {
  if (evaluation.appeal_status === 'resolved') {
    return 'status-resolved'
  }
  
  const now = new Date()
  const deadline = new Date(evaluation.appeal_deadline)
  
  if (now > deadline) {
    return 'status-expired'
  }
  
  return 'status-active'
}

// 跳转到申诉页面
const goToAppeal = (evaluationId) => {
  router.push(`/appeal/${evaluationId}`)
}

// 查看商品详情
const viewProduct = (productId) => {
  router.push(`/product/${productId}`)
}

// 联系买家
const contactBuyer = (buyerId) => {
  // 这里可以跳转到聊天页面或打开聊天窗口
  ElMessage.info('联系买家功能开发中')
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchNegativeEvaluations()
})
</script>

<style scoped>
.negative-evaluations {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.evaluations-card {
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

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-info h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.buyer-info {
  margin: 0;
  color: #666;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.evaluation-details {
  padding: 20px 0;
}

.evaluation-content h4 {
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

.reason-tag {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-left: 10px;
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

.deduction-reasons {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason-chip {
  background-color: #fff0f0;
  color: #f56c6c;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  border: 1px solid #fab6b6;
}

.evidence-section {
  margin: 25px 0;
}

.evidence-section h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
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

.deadline-section {
  background-color: #f0f9ff;
  border: 1px solid #d0e8ff;
  border-radius: 6px;
  padding: 15px;
  margin: 20px 0;
}

.deadline-section h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.deadline-section p {
  margin: 8px 0;
  color: #666;
}

.status-resolved {
  color: #67c23a;
  font-weight: bold;
}

.status-expired {
  color: #f56c6c;
  font-weight: bold;
}

.status-active {
  color: #409eff;
  font-weight: bold;
}

.appeal-response {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

@media (max-width: 768px) {
  .negative-evaluations {
    padding: 10px;
  }
  
  .evaluation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .status-tags {
    flex-wrap: wrap;
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