<!-- frontend/src/views/ProductBrowse.vue -->
<template>
  <div class="product-browse">
    <el-row :gutter="20">
      <el-col :span="24">
        <!-- 搜索栏 -->
        <div class="search-section">
          <el-input
            v-model="searchQuery"
            placeholder="搜索商品..."
            style="width: 300px; margin-right: 20px;"
            @keyup.enter="searchProducts"
          >
            <template #append>
              <el-button icon="Search" @click="searchProducts"></el-button>
            </template>
          </el-input>

          <!-- 分类导航 -->
          <el-radio-group v-model="selectedCategory" @change="filterByCategory">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="book">教材图书</el-radio-button>
            <el-radio-button label="digital">数码产品</el-radio-button>
            <el-radio-button label="life">生活用品</el-radio-button>
            <el-radio-button label="other">其他</el-radio-button>
          </el-radio-group>
        </div>
      </el-col>
    </el-row>

    <!-- 商品网格 -->
    <div class="product-grid">
      <el-row :gutter="20">
        <el-col
          v-for="product in products"
          :key="product.id"
          :span="6"
          style="margin-bottom: 20px;"
        >
          <el-card
            class="product-card"
            @click="viewProductDetail(product.id)"
            shadow="hover"
          >
            <div class="product-image">
              <img
                v-if="product.images"
                :src="product.images.startsWith('http') ? product.images : 'http://127.0.0.1:8000' + product.images"
                alt="商品图片"
              >
              <div v-else class="no-image">暂无图片</div>
            </div>
            <div class="product-info">
              <h3 class="product-title">{{ product.title }}</h3>
              <p class="product-price">¥{{ product.price }}</p>
              <div class="product-meta">
                <div class="seller-info">
                  <span class="seller">{{ product.seller_nickname }}</span>
                  <span 
                    class="credit-badge" 
                    :class="getCreditScoreClass(product.seller_credit_score)"
                  >
                    {{ product.seller_credit_score }}分
                  </span>
                </div>
                <span class="location">{{ product.dormitory_building }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        layout="prev, pager, next"
        :total="totalProducts"
        :page-size="pageSize"
        v-model:current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 获取信用分等级样式
const getCreditScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'fair'
  return 'poor'
}

// 响应式数据
const products = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(4)
const totalProducts = ref(0)

// 获取商品列表
const fetchProducts = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }

    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }

    const response = await axios.get('/api/products/', { params })
    products.value = response.data.results || response.data
    totalProducts.value = response.data.count || products.value.length
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  }
}

// 搜索商品
const searchProducts = () => {
  currentPage.value = 1
  fetchProducts()
}

// 按分类筛选
const filterByCategory = () => {
  currentPage.value = 1
  fetchProducts()
}

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchProducts()
}

// 查看商品详情
const viewProductDetail = (productId) => {
  router.push(`/product/${productId}`)
}

// 组件挂载时获取数据
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-browse {
  padding: 20px;
}

.search-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

/* 自定义单选按钮组样式，使选中时变为紫色 */
:deep(.el-radio-button__inner) {
  color: #606266;
  background-color: #fff;
  border-color: #dcdfe6;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-left: 1px solid #dcdfe6;
}

/* 确保选中状态的样式优先级足够高 */
:deep(.el-radio-button .el-radio-button__orig-radio:checked + .el-radio-button__inner),
:deep(.el-radio-button.is-active .el-radio-button__inner) {
  color: #fff !important;
  background-color: #737BBE !important;
  border-color: #737BBE !important;
  box-shadow: -1px 0 0 0 #737BBE !important;
}

:deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner:hover) {
  color: #fff !important;
  background-color: #737BBE !important;
  border-color: #737BBE !important;
}

:deep(.el-radio-button__inner:hover) {
  color: #737BBE;
}

/* 分页组件样式 */
:deep(.el-pagination .btn-next),
:deep(.el-pagination .btn-prev),
:deep(.el-pagination .el-pager li) {
  color: #737BBE;
}

:deep(.el-pagination .btn-next:hover),
:deep(.el-pagination .btn-prev:hover),
:deep(.el-pagination .el-pager li:hover) {
  color: #6269a9;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background-color: #737BBE !important;
  color: #fff !important;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled):hover) {
  color: #737BBE;
}

.product-grid {
  margin-bottom: 30px;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  height: 200px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
}

.product-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
  font-size: 14px;
}

.product-info {
  padding: 15px 10px 0;
}

.product-title {
  font-size: 16px;
  margin: 0 0 10px 0;
  height: 40px;
  overflow: hidden;
}

.product-price {
  font-size: 18px;
  color: #ff4444;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.credit-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.credit-badge.excellent {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #67c23a;
}

.credit-badge.good {
  background-color: #f0f7ff;
  color: #409eff;
  border: 1px solid #409eff;
}

.credit-badge.fair {
  background-color: #fdf6ec;
  color: #e6a23c;
  border: 1px solid #e6a23c;
}

.credit-badge.poor {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #f56c6c;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>