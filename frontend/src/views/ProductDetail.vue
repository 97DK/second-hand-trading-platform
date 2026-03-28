<!-- frontend/src/views/ProductDetail.vue -->
<template>
  <div class="product-detail">
    <el-row :gutter="30">
      <!-- 商品图片 -->
      <el-col :span="12">
        <div class="image-gallery">
          <el-image
            v-if="product.images"
            :src="product.images.startsWith('http') ? product.images : 'http://127.0.0.1:8000' + product.images"
            fit="cover"
            class="main-image"
          ></el-image>
          <div v-else class="no-image">暂无图片</div>
        </div>
      </el-col>

      <!-- 商品信息 -->
      <el-col :span="12">
        <div class="product-info">
          <h1 class="product-title">{{ product.title }}</h1>

          <div class="product-price">
            <span class="current-price">¥{{ product.price }}</span>
          </div>

          <div class="product-description">
            <h3>商品描述</h3>
            <p>{{ product.description }}</p>
          </div>

          <div class="product-details">
            <el-descriptions :column="1" size="medium">
              <el-descriptions-item label="分类">{{ getCategoryLabel(product.category) }}</el-descriptions-item>
              <el-descriptions-item label="状态">出售中</el-descriptions-item>
              <el-descriptions-item label="位置">{{ product.dormitory_building }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 卖家信息 -->
          <div class="seller-info">
            <h3>卖家信息</h3>
            <div class="seller-profile">
              <el-avatar
                :src="product.seller_avatar ? (product.seller_avatar.startsWith('http') ? product.seller_avatar : 'http://127.0.0.1:8000' + product.seller_avatar) : null"
                size="large"
              >
                {{ product.seller_nickname?.charAt(0) }}
              </el-avatar>
              <div class="seller-details">
                <span class="seller-name">{{ product.seller_nickname }}</span>
                <div class="credit-display">
                  <span class="credit-label">信用分：</span>
                  <span 
                    class="credit-score" 
                    :class="getCreditScoreClass(product.seller_credit_score)"
                  >
                    {{ product.seller_credit_score }}分
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <div v-if="!isOwner && product.status === 'on_sale'" class="purchase-section">
              <div class="quantity-selector">
                <span class="quantity-label">购买数量：</span>
                <el-input-number
                  v-model="purchaseQuantity"
                  :min="1"
                  :controls="true"
                  controls-position="right"
                  size="large"
                  @change="handleQuantityChange"
                />
                <span class="inventory-info">(库存: {{ product.inventory }}件)</span>
              </div>
              <el-button 
                type="primary" 
                size="large" 
                @click="purchaseProduct" 
                :disabled="isOwner || product.status !== 'on_sale' || purchaseQuantity <= 0 || purchaseQuantity > product.inventory || !product.inventory"
                :class="{ 'purchase-disabled': purchaseQuantity <= 0 || purchaseQuantity > product.inventory || isOwner || product.status !== 'on_sale' || !product.inventory }"
              >
                {{ getPurchaseButtonText() }}
              </el-button>
            </div>
            <el-button 
              v-if="isBuyer && !hasEvaluation" 
              type="success" 
              size="large" 
              @click="showEvaluationDialog"
            >
              去评价
            </el-button>
            <el-button 
              v-else-if="isBuyer && hasEvaluation" 
              type="info" 
              size="large" 
              @click="showEvaluationDetail"
            >
              已评价
            </el-button>
            <el-button 
              type="primary" 
              size="large" 
              @click="showContactDialog"
            >
              <el-icon><ChatDotRound /></el-icon>
              联系卖家
            </el-button>
            <el-button size="large" @click="toggleFavorite">
              <el-icon><Star v-if="isFavorited" /><StarFilled v-else /></el-icon>
              收藏
            </el-button>
            <el-button type="danger" size="large" plain @click="reportProduct">
              <el-icon><Warning /></el-icon>
              举报
            </el-button>
          </div>
          
          <!-- 如果是自己的商品，则显示提示 -->
          <div v-if="isOwner" class="owner-notice">
            这是你发布的商品，无法购买
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 联系卖家对话框 -->
    <el-dialog v-model="contactDialogVisible" title="联系卖家" width="40%">
      <el-form>
        <el-form-item label="消息内容">
          <el-input
            v-model="contactMessage"
            type="textarea"
            :rows="4"
            placeholder="请输入您想对卖家说的话"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="contactDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="contactSeller">发送</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 商品评价对话框 -->
    <el-dialog v-model="evaluationDialogVisible" title="商品评价" width="500px">
      <div class="evaluation-header">
        <h3>感谢您的购买！请对本次交易进行评价：</h3>
        <p>您的评价将帮助其他用户更好地了解卖家</p>
      </div>
      
      <el-form :model="evaluationForm" label-width="150px">
        <el-form-item label="是否收到货？" required>
          <el-radio-group v-model="evaluationForm.received_item">
            <el-radio label="yes">是</el-radio>
            <el-radio label="no">否</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="是否与商品描述一致？" required>
          <el-radio-group v-model="evaluationForm.description_match">
            <el-radio label="yes">是</el-radio>
            <el-radio label="no">否</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="商家服务态度？" required>
          <el-radio-group v-model="evaluationForm.service_attitude">
            <el-radio label="yes">是</el-radio>
            <el-radio label="no">否</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 证据照片上传区域 -->
        <el-form-item 
          v-if="needsEvidencePhotos" 
          label="证据照片" 
          required
          prop="evidence_photos"
        >
          <div class="photo-upload-section">
            <p class="upload-hint">
              ⚠️ 您选择了"否"，请上传相关证据照片以支持您的评价
            </p>
            <el-upload
              v-model:file-list="evidencePhotos"
              list-type="picture-card"
              :auto-upload="false"
              :limit="5"
              :on-exceed="handlePhotoExceed"
              :on-remove="handlePhotoRemove"
              :on-change="handlePhotoChange"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <p class="upload-tip">最多可上传5张照片，支持JPG/PNG格式</p>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="evaluationDialogVisible = false">稍后评价</el-button>
          <el-button 
            type="primary" 
            @click="submitEvaluation" 
            :loading="evaluationLoading"
            :disabled="!isEvaluationValid"
          >
            提交评价
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, Star, StarFilled, Warning, Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const product = ref({})
const isFavorited = ref(false)
const purchaseQuantity = ref(1)

// 联系卖家相关
const contactDialogVisible = ref(false)
const contactMessage = ref('')

// 商品评价相关
const evaluationDialogVisible = ref(false)
const evaluationLoading = ref(false)
const evaluationForm = ref({
  received_item: '',
  description_match: '',
  service_attitude: '',
  evidence_photos: []
})
const evidencePhotos = ref([])

// 计算属性：判断当前用户是否为商品所有者
const isOwner = computed(() => {
  return authStore.isAuthenticated && authStore.user && 
         product.value.seller === authStore.user.id
})

// 计算属性：判断当前用户是否为购买者
const isBuyer = computed(() => {
  return authStore.isAuthenticated && authStore.user && 
         product.value.buyer === authStore.user.id && 
         product.value.status === 'sold'
})

// 计算属性：判断是否已有评价
const hasEvaluation = computed(() => {
  // 这里可以根据实际需求来判断，暂时返回false
  return false
})

// 计算属性：判断评价表单是否完整
const isEvaluationValid = computed(() => {
  return evaluationForm.value.received_item && 
         evaluationForm.value.description_match && 
         evaluationForm.value.service_attitude
})

// 计算属性：判断是否需要上传证据照片
const needsEvidencePhotos = computed(() => {
  return (evaluationForm.value.received_item === 'no' || 
          evaluationForm.value.description_match === 'no' || 
          evaluationForm.value.service_attitude === 'no')
})

// 获取分类标签
const getCategoryLabel = (category) => {
  const categories = {
    'book': '教材图书',
    'digital': '数码产品',
    'life': '生活用品',
    'other': '其他'
  }
  return categories[category] || category
}

// 获取信用分等级样式
const getCreditScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'fair'
  return 'poor'
}

// 获取购买按钮文本
const getPurchaseButtonText = () => {
  if (isOwner.value) {
    return '无法购买'
  }
  if (product.value.status !== 'on_sale') {
    return '商品不可购买'
  }
  if (!product.value.inventory || product.value.inventory <= 0) {
    return '库存不足'
  }
  if (purchaseQuantity.value <= 0) {
    return '请输入购买数量'
  }
  if (purchaseQuantity.value > product.value.inventory) {
    return '超出库存'
  }
  return '立即购买'
}

// 获取商品详情
const fetchProductDetail = async () => {
  try {
    const response = await axios.get(`/api/products/${route.params.id}/`)
    product.value = response.data
  } catch (error) {
    ElMessage.error('获取商品详情失败')
    router.back()
  }
}

// 处理购买数量变更
const handleQuantityChange = (value) => {
  // 验证输入值的有效性
  if (value === null || value === undefined || value === '') {
    ElMessage.warning('请输入有效的数字')
    purchaseQuantity.value = 1
    return
  }
  
  // 处理字符串输入
  let numValue;
  try {
    numValue = parseInt(value);
    if (isNaN(numValue)) {
      throw new Error('Invalid number');
    }
  } catch (e) {
    ElMessage.warning('请输入有效的整数')
    purchaseQuantity.value = 1
    return
  }
  
  // 特殊处理：如果输入为0，给出明确提示
  if (numValue === 0) {
    ElMessage.warning('购买数量不能为0，请输入大于0的数字')
    // 不自动重置，让用户自己修改
    return
  }
  
  // 处理负数情况
  if (numValue < 0) {
    ElMessage.warning('购买数量不能为负数，请输入大于0的数字')
    // 不自动重置，让用户自己修改
    return
  }
  
  // 保留用户输入值
  purchaseQuantity.value = numValue
}

// 购买商品
const purchaseProduct = async () => {
  try {
    // 关键：在每次购买前都强制验证当前库存
    await fetchProductDetail(); // 重新获取最新库存信息
    
    // 前端验证购买数量
    if (purchaseQuantity.value <= 0) {
      ElMessage.error('购买数量必须大于0')
      purchaseQuantity.value = 1
      return
    }
    
    if (purchaseQuantity.value > product.value.inventory) {
      // 修改为弹窗提示而不是自动修改数量
      await ElMessageBox.alert(
        `不可购买数量大于库存，请修改后再购买\n当前库存：${product.value.inventory}件\n您输入的数量：${purchaseQuantity.value}件`,
        '购买数量超出库存',
        {
          confirmButtonText: '我知道了',
          type: 'warning',
        }
      )
      return
    }
    
    // 额外的保险验证
    if (typeof product.value.inventory !== 'number' || product.value.inventory < 0) {
      ElMessage.error('商品库存信息异常，请刷新页面后重试')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要购买 "${product.value.title}" 吗？\n数量：${purchaseQuantity.value}件\n单价：¥${product.value.price}\n总价：¥${(product.value.price * purchaseQuantity.value).toFixed(2)}`,
      '确认购买',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await axios.post(`/api/products/${route.params.id}/purchase/`, {
      quantity: purchaseQuantity.value
    })
    
    if (response.data.success) {
      ElMessage.success('购买成功！')
      // 刷新商品信息
      fetchProductDetail()
      
      // 更新用户余额信息
      try {
        const userResponse = await axios.get('/api/users/profile/')
        authStore.user.balance = userResponse.data.balance
      } catch (error) {
        console.error('更新用户余额失败:', error)
      }
      
      // 不再自动弹出评价对话框，用户可在个人中心进行评价
    } else {
      ElMessage.error(response.data.error || '购买失败')
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(error.response.data.error)
    } else if (error.message !== 'cancel') {
      ElMessage.error('购买过程中出现错误')
    }
  }
}

// 显示联系卖家对话框
const showContactDialog = () => {
  contactMessage.value = '我想了解这个商品'
  contactDialogVisible.value = true
}

// 联系卖家
const contactSeller = async () => {
  try {
    await axios.post(`/api/products/contact/seller/${route.params.id}/`, {
      content: contactMessage.value
    })
    
    ElMessage.success('消息已发送给卖家')
    contactDialogVisible.value = false
  } catch (error) {
    ElMessage.error('发送失败')
  }
}

// 切换收藏状态
const toggleFavorite = () => {
  isFavorited.value = !isFavorited.value
  ElMessage.success(isFavorited.value ? '已收藏' : '已取消收藏')
}

// 举报商品
const reportProduct = () => {
  ElMessageBox.prompt('请输入举报原因', '举报商品', {
    confirmButtonText: '提交',
    cancelButtonText: '取消',
    inputPattern: /\S/,
    inputErrorMessage: '举报原因不能为空'
  }).then(({ value }) => {
    ElMessage.success('举报已提交，我们会尽快处理')
  }).catch(() => {
    // 取消操作
  })
}

// 显示评价对话框
const showEvaluationDialog = () => {
  // 重置表单
  evaluationForm.value = {
    received_item: '',
    description_match: '',
    service_attitude: '',
    evidence_photos: []
  }
  evidencePhotos.value = []
  evaluationDialogVisible.value = true
}

// 照片上传处理函数
const handlePhotoExceed = () => {
  ElMessage.warning('最多只能上传5张照片')
}

const handlePhotoRemove = (file, fileList) => {
  evidencePhotos.value = fileList
  // 更新表单数据
  evaluationForm.value.evidence_photos = fileList.map(file => ({
    name: file.name,
    url: file.url || URL.createObjectURL(file.raw)
  }))
}

const handlePhotoChange = (file, fileList) => {
  evidencePhotos.value = fileList
  // 更新表单数据
  evaluationForm.value.evidence_photos = fileList.map(file => ({
    name: file.name,
    url: file.url || URL.createObjectURL(file.raw)
  }))
}

// 提交商品评价
const submitEvaluation = async () => {
  if (!isEvaluationValid.value) {
    ElMessage.warning('请完成所有评价项')
    return
  }
  
  // 检查负面评价是否上传了证据照片
  if (needsEvidencePhotos.value && (!evaluationForm.value.evidence_photos || evaluationForm.value.evidence_photos.length === 0)) {
    ElMessage.warning('当选择"否"时，必须上传至少一张证据照片')
    return
  }
  
  evaluationLoading.value = true
  try {
    const response = await axios.post(`/api/products/${route.params.id}/evaluate/`, evaluationForm.value)
    
    if (response.data.success) {
      ElMessage.success(`评价提交成功${response.data.deduction_points > 0 ? '，本次评价扣分' + response.data.deduction_points + '分' : ''}`)
      evaluationDialogVisible.value = false
      
      // 如果有扣分，提示用户
      if (response.data.deduction_points > 0) {
        ElMessage.warning('由于您的负面评价，相关卖家的信用分已被扣除')
      }
    }
  } catch (error) {
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('评价提交失败')
    }
  } finally {
    evaluationLoading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchProductDetail()
  
  // 处理来自个人主页的评价跳转
  const checkForEvaluationHash = () => {
    if (window.location.hash === '#evaluate' && isBuyer.value && !hasEvaluation.value) {
      // 延迟显示评价对话框，确保页面加载完成
      setTimeout(() => {
        showEvaluationDialog()
        // 清除hash
        history.replaceState(null, null, window.location.pathname)
      }, 800)
    }
  }
  
  // 立即检查
  checkForEvaluationHash()
  
  // 监听hash变化
  window.addEventListener('hashchange', checkForEvaluationHash)
  
  // 组件卸载时移除监听器
  onUnmounted(() => {
    window.removeEventListener('hashchange', checkForEvaluationHash)
  })
})
</script>

<style scoped>
.product-detail {
  padding: 20px;
}

.image-gallery {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.main-image {
  max-width: 100%;
  max-height: 100%;
}

.no-image {
  color: #999;
  font-size: 18px;
}

.product-info {
  padding: 20px;
}

.product-title {
  font-size: 24px;
  margin-bottom: 20px;
}

.product-price {
  margin-bottom: 30px;
}

.current-price {
  font-size: 32px;
  color: #ff4444;
  font-weight: bold;
}

.product-description h3,
.product-details h3,
.seller-info h3 {
  margin-top: 30px;
  margin-bottom: 15px;
  font-size: 18px;
}

.product-description p {
  line-height: 1.6;
  color: #666;
}

.seller-profile {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.seller-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.seller-name {
  font-size: 16px;
  font-weight: bold;
}

.credit-display {
  display: flex;
  align-items: center;
  gap: 5px;
}

.credit-label {
  font-size: 14px;
  color: #909399;
}

.credit-score {
  font-size: 14px;
  font-weight: bold;
}

.credit-score.excellent {
  color: #67c23a;
}

.credit-score.good {
  color: #409eff;
}

.credit-score.fair {
  color: #e6a23c;
}

.credit-score.poor {
  color: #f56c6c;
}

.action-buttons {
  margin-top: 40px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.purchase-section {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.inventory-info {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.owner-notice {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
  text-align: center;
}

.evaluation-header {
  text-align: center;
  margin-bottom: 20px;
}

.evaluation-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.evaluation-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.photo-upload-section {
  width: 100%;
}

.upload-hint {
  color: #e6a23c;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 500;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 10px;
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 评价详情样式 */
.evaluation-detail {
  padding: 20px;
}

.evaluation-detail h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
  text-align: center;
}

.evaluation-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.evaluation-item label {
  display: inline-block;
  width: 150px;
  font-weight: bold;
  color: #606266;
}

.evaluation-positive {
  color: #67c23a;
  font-weight: bold;
}

.evaluation-negative {
  color: #f56c6c;
  font-weight: bold;
}

.evaluation-time {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
  color: #909399;
  font-size: 14px;
  text-align: center;
}

/* 购买按钮禁用状态样式 */
.purchase-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.purchase-disabled:hover {
  opacity: 0.6;
  transform: none;
}
</style>