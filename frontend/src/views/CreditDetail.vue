<!-- frontend/src/views/CreditDetail.vue -->
<template>
  <div class="credit-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>我的信用分详情</h2>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>
      
      <!-- 信用分概览 -->
      <div class="credit-overview">
        <div class="score-display">
          <div class="score-circle" :class="scoreClass">
            {{ creditScore }}
          </div>
          <div class="score-info">
            <h3>{{ scoreMessage }}</h3>
            <p class="score-description">{{ scoreDescription }}</p>
          </div>
        </div>
      </div>
      
      <!-- 扣分记录 -->
      <div class="deduction-section">
        <h3>扣分记录</h3>
        <el-table 
          :data="deductionRecords" 
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="reason_display" label="扣分原因" width="150" />
          <el-table-column prop="deduction_points" label="扣分数" width="100">
            <template #default="{ row }">
              <span class="deduction-points">-{{ row.deduction_points }}分</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="详情" />
          <el-table-column prop="appeal_status_display" label="申诉状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getAppealStatusType(row.appeal_status)">
                {{ row.appeal_status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button 
                v-if="row.appeal_status === 'pending'" 
                size="small" 
                type="primary"
                @click="showAppealDialog(row)"
              >
                申诉
              </el-button>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty 
          v-if="!loading && deductionRecords.length === 0" 
          description="暂无扣分记录" 
        />
      </div>
    </el-card>
    
    <!-- 申诉对话框 -->
    <el-dialog v-model="appealDialogVisible" title="提交申诉" width="500px">
      <el-form :model="appealForm" label-width="80px">
        <el-form-item label="扣分原因">
          <el-input 
            v-model="currentDeduction.reason_display" 
            disabled 
          />
        </el-form-item>
        <el-form-item label="扣分数">
          <el-input 
            v-model="currentDeduction.deduction_points" 
            disabled
          >
            <template #append>分</template>
          </el-input>
        </el-form-item>
        <el-form-item label="申诉理由" required>
          <el-input
            v-model="appealForm.appeal_content"
            type="textarea"
            :rows="4"
            placeholder="请输入申诉理由..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="appealDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAppeal" :loading="appealLoading">
            提交申诉
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 响应式数据
const creditScore = ref(100)
const deductionRecords = ref([])
const loading = ref(false)
const appealDialogVisible = ref(false)
const appealLoading = ref(false)
const currentDeduction = ref({})

const appealForm = ref({
  appeal_content: ''
})

// 计算属性
const scoreClass = computed(() => {
  if (creditScore.value === 100) return 'perfect'
  if (creditScore.value >= 80) return 'good'
  if (creditScore.value >= 60) return 'fair'
  return 'poor'
})

const scoreMessage = computed(() => {
  if (creditScore.value === 100) return '您的信用极佳，请继续保持！'
  if (creditScore.value >= 80) return '您的信用良好'
  if (creditScore.value >= 60) return '您的信用一般'
  return '您的信用较差，请注意改善'
})

const scoreDescription = computed(() => {
  if (creditScore.value === 100) return '恭喜您保持了完美的信用记录！'
  return '信用分反映了您的交易信誉，良好的信用有助于获得更多交易机会。'
})

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取申诉状态标签类型
const getAppealStatusType = (status) => {
  const types = {
    'pending': 'info',
    'submitted': 'warning',
    'resolved': 'success'
  }
  return types[status] || 'info'
}

// 获取信用分
const fetchCreditScore = async () => {
  try {
    const response = await axios.get('/api/users/credit-score/')
    creditScore.value = response.data.credit_score
  } catch (error) {
    ElMessage.error('获取信用分失败')
  }
}

// 获取扣分记录
const fetchDeductionRecords = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/users/credit-deductions/')
    deductionRecords.value = response.data
  } catch (error) {
    ElMessage.error('获取扣分记录失败')
  } finally {
    loading.value = false
  }
}

// 显示申诉对话框
const showAppealDialog = (record) => {
  currentDeduction.value = record
  appealForm.value.appeal_content = ''
  appealDialogVisible.value = true
}

// 提交申诉
const submitAppeal = async () => {
  if (!appealForm.value.appeal_content.trim()) {
    ElMessage.warning('请输入申诉理由')
    return
  }
  
  appealLoading.value = true
  try {
    const response = await axios.post(
      `/api/users/credit-appeal/${currentDeduction.value.id}/`,
      appealForm.value
    )
    
    ElMessage.success('申诉提交成功')
    appealDialogVisible.value = false
    fetchDeductionRecords() // 刷新记录
  } catch (error) {
    ElMessage.error('申诉提交失败')
  } finally {
    appealLoading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchCreditScore()
  fetchDeductionRecords()
})
</script>

<style scoped>
.credit-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.credit-overview {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.score-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  color: white;
}

.score-circle.perfect {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.score-circle.good {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.score-circle.fair {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.score-circle.poor {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.score-info h3 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.score-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.deduction-section h3 {
  margin-bottom: 20px;
  color: #303133;
}

.deduction-points {
  color: #f56c6c;
  font-weight: bold;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>