<!-- frontend/src/views/AdminWishManagement.vue -->
<template>
  <div class="admin-wish-management">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="待审核心愿" name="pending">
        <el-table :data="pendingWishes" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="心愿标题"></el-table-column>
          <el-table-column prop="user.username" label="发布者"></el-table-column>
          <el-table-column prop="created_at" label="发布时间"></el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" type="success" @click="approveWish(row.id)">通过</el-button>
              <el-button size="small" type="danger" @click="showRejectDialog(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="已通过心愿" name="approved">
        <el-table :data="approvedWishes" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="心愿标题"></el-table-column>
          <el-table-column prop="user.username" label="发布者"></el-table-column>
          <el-table-column prop="created_at" label="发布时间"></el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" type="warning" @click="markAsFulfilled(row.id)">标记为已实现</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="被拒绝心愿" name="rejected">
        <el-table :data="rejectedWishes" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="心愿标题"></el-table-column>
          <el-table-column prop="user.username" label="发布者"></el-table-column>
          <el-table-column prop="reject_reason" label="拒绝原因"></el-table-column>
          <el-table-column prop="created_at" label="发布时间"></el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 拒绝原因对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝心愿" width="500px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        placeholder="请输入拒绝理由"
        :rows="4"
      ></el-input>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="rejectWish">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('pending')
const pendingWishes = ref([])
const approvedWishes = ref([])
const rejectedWishes = ref([])
const loading = ref(false)

// 拒绝对话框相关
const rejectDialogVisible = ref(false)
const currentWishId = ref(null)
const rejectReason = ref('')

const fetchPendingWishes = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/products/admin/wishes/?type=pending')
    pendingWishes.value = response.data
  } catch (error) {
    ElMessage.error('获取待审核心愿失败')
  } finally {
    loading.value = false
  }
}

const fetchApprovedWishes = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/products/admin/wishes/?type=approved')
    approvedWishes.value = response.data
  } catch (error) {
    ElMessage.error('获取已通过心愿失败')
  } finally {
    loading.value = false
  }
}

const fetchRejectedWishes = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/products/admin/wishes/?type=rejected')
    rejectedWishes.value = response.data
  } catch (error) {
    ElMessage.error('获取被拒绝心愿失败')
  } finally {
    loading.value = false
  }
}

const approveWish = async (wishId) => {
  try {
    await axios.post('/api/products/admin/wishes/', {
      wish_id: wishId,
      action: 'approve'
    })
    ElMessage.success('心愿审核通过')
    fetchPendingWishes()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const showRejectDialog = (wishId) => {
  currentWishId.value = wishId
  rejectDialogVisible.value = true
  rejectReason.value = ''
}

const rejectWish = async () => {
  try {
    await axios.post('/api/products/admin/wishes/', {
      wish_id: currentWishId.value,
      action: 'reject',
      reason: rejectReason.value
    })
    ElMessage.success('心愿已拒绝')
    rejectDialogVisible.value = false
    fetchPendingWishes()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const markAsFulfilled = async (wishId) => {
  try {
    await axios.patch(`/api/products/wishes/${wishId}/`, {
      is_fulfilled: true
    })
    ElMessage.success('心愿已标记为已实现')
    fetchApprovedWishes()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleTabChange = (tab) => {
  switch(tab) {
    case 'pending':
      fetchPendingWishes()
      break
    case 'approved':
      fetchApprovedWishes()
      break
    case 'rejected':
      fetchRejectedWishes()
      break
  }
}

onMounted(() => {
  fetchPendingWishes()
})
</script>

<style scoped>
/* 样式可以根据需要添加 */
</style>
