<template>
  <div class="admin-user-management">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="待审核用户" name="pending">
        <el-table :data="pendingUsers" style="width: 100%" v-loading="loading">
          <el-table-column prop="student_id" label="学号"></el-table-column>
          <el-table-column prop="username" label="用户名"></el-table-column>
          <el-table-column prop="date_joined" label="注册时间"></el-table-column>
          <el-table-column label="学生证">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                @click="viewStudentCard(row)"
                :disabled="!row.student_card_photo">
                查看图片
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" type="success" @click="approveUser(row.id)">通过</el-button>
              <el-button size="small" type="danger" @click="rejectUser(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="已审核用户" name="verified">
        <el-input v-model="searchKeyword" placeholder="搜索用户..." style="margin-bottom: 20px; width: 300px;">
          <template #append>
            <el-button icon="Search" @click="searchUsers"></el-button>
          </template>
        </el-input>
        <el-table :data="verifiedUsers" style="width: 100%" v-loading="loading">
          <el-table-column prop="student_id" label="学号"></el-table-column>
          <el-table-column prop="username" label="用户名"></el-table-column>
          <el-table-column prop="is_verified" label="状态">
            <template #default="{ row }">
              <el-tag v-if="row.is_verified" type="success">已审核</el-tag>
              <el-tag v-else type="warning">未审核</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="学生证">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                @click="viewStudentCard(row)"
                :disabled="!row.student_card_photo">
                查看图片
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" type="warning" @click="banUser(row.id)">封禁</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用户统计" name="stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-item">
              <div class="stat-number">{{ userStats.total_users || 0 }}</div>
              <div class="stat-label">总用户数</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-item">
              <div class="stat-number">{{ userStats.student_users || 0 }}</div>
              <div class="stat-label">学生用户</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-item">
              <div class="stat-number">{{ userStats.verified_students || 0 }}</div>
              <div class="stat-label">已认证学生</div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-item">
              <div class="stat-number">{{ userStats.pending_students || 0 }}</div>
              <div class="stat-label">待审核学生</div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- Student Card Image Preview Dialog -->
    <el-dialog v-model="imageDialogVisible" title="学生证照片" width="500px">
      <div style="text-align: center;">
        <el-image
          v-if="currentStudentCardUrl"
          :src="currentStudentCardUrl"
          style="max-width: 100%; max-height: 400px"
          fit="contain"
          :preview-src-list="[currentStudentCardUrl]"
          preview-teleported
        />
        <p v-else>无学生证照片</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="imageDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('pending')
const pendingUsers = ref([])
const verifiedUsers = ref([])
const userStats = ref({})
const loading = ref(false)
const searchKeyword = ref('')

// Image preview dialog
const imageDialogVisible = ref(false)
const currentStudentCardUrl = ref('')

const fetchPendingUsers = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/users/admin/users/?type=pending')
    pendingUsers.value = response.data
  } catch (error) {
    ElMessage.error('获取待审核用户失败')
  } finally {
    loading.value = false
  }
}

const fetchVerifiedUsers = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/users/admin/users/?type=verified')
    verifiedUsers.value = response.data
  } catch (error) {
    ElMessage.error('获取已审核用户失败')
  } finally {
    loading.value = false
  }
}

const fetchUserStats = async () => {
  try {
    const response = await axios.get('/api/users/admin/user-stats/')
    userStats.value = response.data
  } catch (error) {
    ElMessage.error('获取用户统计数据失败')
  }
}

const approveUser = async (userId) => {
  try {
    await axios.post(`/api/users/admin/users/${userId}/approve/`)
    ElMessage.success('用户审核通过')
    refreshCurrentTab()
    // 同时刷新另一个选项卡和统计数据
    fetchVerifiedUsers()
    fetchUserStats()
  } catch (error) {
    ElMessage.error('审核操作失败')
  }
}

const rejectUser = async (userId) => {
  try {
    await axios.post(`/api/users/admin/users/${userId}/reject/`)
    ElMessage.success('用户审核拒绝')
    refreshCurrentTab()
    // 同时刷新统计数据
    fetchUserStats()
  } catch (error) {
    ElMessage.error('拒绝操作失败')
  }
}

const banUser = async (userId) => {
  try {
    await axios.post(`/api/users/admin/users/${userId}/ban/`)
    ElMessage.success('用户已封禁')
    refreshCurrentTab()
  } catch (error) {
    ElMessage.error('封禁操作失败')
  }
}

const searchUsers = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/api/users/admin/users/?search=${searchKeyword.value}`)
    verifiedUsers.value = response.data
  } catch (error) {
    ElMessage.error('搜索用户失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = (tabName) => {
  if (tabName === 'pending') {
    fetchPendingUsers()
  } else if (tabName === 'verified') {
    fetchVerifiedUsers()
  } else if (tabName === 'stats') {
    fetchUserStats()
  }
}

const refreshCurrentTab = () => {
  if (activeTab.value === 'pending') {
    fetchPendingUsers()
  } else if (activeTab.value === 'verified') {
    fetchVerifiedUsers()
  }
}

const viewStudentCard = (user) => {
  if (user.student_card_photo) {
    currentStudentCardUrl.value = `http://127.0.0.1:8000${user.student_card_photo}`
    imageDialogVisible.value = true
  } else {
    ElMessage.info('该用户未上传学生证照片')
  }
}

onMounted(() => {
  fetchPendingUsers()
  fetchUserStats()
})
</script>

<style scoped>
.admin-user-management {
  padding: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}
</style>