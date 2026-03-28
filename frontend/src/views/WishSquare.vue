<!-- frontend/src/views/WishSquare.vue -->
<template>
  <div class="wish-square">
    <el-row :gutter="20">
      <el-col :span="18">
        <div class="wish-list">
          <div 
            v-for="wish in wishes" 
            :key="wish.id" 
            class="wish-item"
          >
            <el-card>
              <div class="wish-content">
                <h3 class="wish-title">{{ wish.title }}</h3>
                <p class="wish-description">{{ wish.description }}</p>
                
                <div class="wish-meta">
                  <span class="max-price" v-if="wish.max_price">预算：¥{{ wish.max_price }}</span>
                  <span class="max-price" v-else>预算：无限制</span>
                </div>

                <div class="user-info">
                  <el-avatar
                    :src="wish.user_avatar ? (wish.user_avatar.startsWith('http') ? wish.user_avatar : 'http://127.0.0.1:8000' + wish.user_avatar) : null"
                    size="small"
                  >
                    {{ wish.user_nickname?.charAt(0) }}
                  </el-avatar>
                  <span class="user-name">{{ wish.user_nickname }}</span>
                </div>

                <div class="wish-actions">
                  <el-button size="small" @click="showContactDialog(wish)">
                    <el-icon><ChatDotRound /></el-icon>
                    联系TA
                  </el-button>
                  <el-button size="small" @click="reportWish(wish)">
                    <el-icon><Warning /></el-icon>
                    举报
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              layout="prev, pager, next"
              :total="totalWishes"
              :page-size="pageSize"
              v-model:current-page="currentPage"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </el-col>

      <el-col :span="6">
        <el-card class="publish-wish-card">
          <template #header>
            <strong>发布心愿</strong>
          </template>
          <p>有想要的物品但暂时找不到？快来发布心愿单，让同学们帮你一起寻找！</p>
          <el-button type="primary" @click="goToPublishWish">发布心愿</el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 联系心愿发布者对话框 -->
    <el-dialog v-model="contactDialogVisible" title="联系心愿发布者" width="40%">
      <el-form>
        <el-form-item label="消息内容">
          <el-input
            v-model="contactMessage"
            type="textarea"
            :rows="4"
            placeholder="请输入您想对心愿发布者说的话"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="contactDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="contactWishUser">发送</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, Warning } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const wishes = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalWishes = ref(0)

// 联系心愿发布者相关
const contactDialogVisible = ref(false)
const contactMessage = ref('')
const currentWish = ref(null)

// 获取心愿列表
const fetchWishes = async () => {
  try {
    const response = await axios.get('/api/products/wishes/', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    wishes.value = response.data.results || response.data
    totalWishes.value = response.data.count || wishes.value.length
  } catch (error) {
    ElMessage.error('获取心愿列表失败')
  }
}

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchWishes()
}

// 显示联系心愿发布者对话框
const showContactDialog = (wish) => {
  currentWish.value = wish
  contactMessage.value = '我有你想要的商品'
  contactDialogVisible.value = true
}

// 联系心愿发布者
const contactWishUser = async () => {
  try {
    await axios.post(`/api/products/contact/wish-user/${currentWish.value.id}/`, {
      content: contactMessage.value
    })
    
    ElMessage.success('消息已发送给心愿发布者')
    contactDialogVisible.value = false
  } catch (error) {
    ElMessage.error('发送失败')
  }
}

// 举报心愿
const reportWish = (wish) => {
  ElMessageBox.prompt('请输入举报原因', '举报心愿', {
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

// 跳转到发布心愿页面
const goToPublishWish = () => {
  router.push('/publish-wish')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchWishes()
})
</script>

<style scoped>
.wish-square {
  padding: 20px;
}

.wish-item {
  margin-bottom: 20px;
}

.wish-content {
  padding: 15px;
}

.wish-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.wish-description {
  margin: 10px 0;
  color: #666;
  line-height: 1.5;
}

.wish-meta {
  margin: 10px 0;
  font-size: 14px;
  color: #999;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.wish-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.publish-wish-card :deep(.el-button) {
  width: 100%;
  margin-top: 10px;
  background-color: #737BBE;
  border-color: #737BBE;
  color: white;
}

.publish-wish-card :deep(.el-button:hover) {
  background-color: #6269a9;
  border-color: #6269a9;
  color: white;
}

.publish-wish-card :deep(.el-button:focus) {
  background-color: #737BBE;
  border-color: #737BBE;
  color: white;
}
</style>