<template>
  <div class="admin-product-management">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="待审核商品" name="pending">
        <el-table :data="pendingProducts" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="商品名称"></el-table-column>
          <el-table-column prop="seller.username" label="卖家"></el-table-column>
          <el-table-column prop="price" label="价格"></el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" type="success" @click="approveProduct(row.id)">通过</el-button>
              <el-button size="small" type="danger" @click="showRejectDialog(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="已上架商品" name="approved">
        <el-table :data="approvedProducts" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="商品名称"></el-table-column>
          <el-table-column prop="seller.username" label="卖家"></el-table-column>
          <el-table-column prop="price" label="价格"></el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="removeProduct(row.id)">下架</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="违规商品" name="rejected">
        <el-table :data="rejectedProducts" style="width: 100%" v-loading="loading">
          <el-table-column prop="title" label="商品名称"></el-table-column>
          <el-table-column prop="seller.username" label="卖家"></el-table-column>
          <el-table-column prop="price" label="价格"></el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'removed'" type="danger">已下架</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 拒绝理由对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝商品" width="500px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        placeholder="请输入拒绝理由"
        :rows="4"
      ></el-input>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="rejectProduct">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('pending')
const pendingProducts = ref([])
const approvedProducts = ref([])
const rejectedProducts = ref([])
const loading = ref(false)

// 拒绝对话框相关
const rejectDialogVisible = ref(false)
const currentProductId = ref(null)
const rejectReason = ref('')

const fetchPendingProducts = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/products/admin/?type=pending')
    pendingProducts.value = response.data
  } catch (error) {
    ElMessage.error('获取待审核商品失败')
  } finally {
    loading.value = false
  }
}

const fetchApprovedProducts = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/products/admin/?type=approved')
    approvedProducts.value = response.data
  } catch (error) {
    ElMessage.error('获取已审核商品失败')
  } finally {
    loading.value = false
  }
}

const fetchRejectedProducts = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/products/admin/?type=rejected')
    rejectedProducts.value = response.data
  } catch (error) {
    ElMessage.error('获取违规商品失败')
  } finally {
    loading.value = false
  }
}

const approveProduct = async (productId) => {
  try {
    await axios.post('/api/products/admin/', {
      product_id: productId,
      action: 'approve'
    })
    ElMessage.success('商品审核通过')
    fetchPendingProducts()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const showRejectDialog = (productId) => {
  currentProductId.value = productId
  rejectDialogVisible.value = true
  rejectReason.value = ''
}

const rejectProduct = async () => {
  try {
    await axios.post('/api/products/admin/', {
      product_id: currentProductId.value,
      action: 'reject',
      reason: rejectReason.value
    })
    ElMessage.success('商品已拒绝')
    rejectDialogVisible.value = false
    fetchPendingProducts()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const removeProduct = async (productId) => {
  try {
    await axios.post('/api/products/admin/', {
      product_id: productId,
      action: 'remove'
    })
    ElMessage.success('商品已下架')
    fetchApprovedProducts()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleTabChange = (tab) => {
  switch(tab) {
    case 'pending':
      fetchPendingProducts()
      break
    case 'approved':
      fetchApprovedProducts()
      break
    case 'rejected':
      fetchRejectedProducts()
      break
  }
}

onMounted(() => {
  fetchPendingProducts()
})
</script>

<style scoped>
/* 样式可以根据需要添加 */
</style>
