<template>
  <div class="admin-analytics">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-number">{{ analyticsData.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-number">{{ analyticsData.total_products }}</div>
            <div class="stat-label">商品总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-number">{{ analyticsData.on_sale_products }}</div>
            <div class="stat-label">在售商品</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <div class="stat-number">{{ analyticsData.sold_products }}</div>
            <div class="stat-label">已售商品</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 30px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户增长趋势</span>
            </div>
          </template>
          <div ref="userChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>商品分类分布</span>
            </div>
          </template>
          <div ref="productChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const analyticsData = ref({})
const userChart = ref(null)
const productChart = ref(null)

const fetchAnalyticsData = async () => {
  try {
    const response = await axios.get('/api/users/admin/analytics/')
    analyticsData.value = response.data

    // 初始化图表
    initCharts()
  } catch (error) {
    ElMessage.error('获取分析数据失败')
  }
}

const initCharts = () => {
  // 用户增长趋势图
  const userChartInstance = echarts.init(userChart.value)
  userChartInstance.setOption({
    title: {
      text: '用户增长趋势'
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: [120, 200, 150, 80, 70, 110],
      type: 'line'
    }]
  })

  // 商品分类分布图
  const productChartInstance = echarts.init(productChart.value)
  productChartInstance.setOption({
    title: {
      text: '商品分类分布'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: '教材图书' },
        { value: 735, name: '数码产品' },
        { value: 580, name: '生活用品' },
        { value: 484, name: '其他' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

onMounted(() => {
  fetchAnalyticsData()
})
</script>

<style scoped>
.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  margin-top: 10px;
  color: #909399;
}

.card-header {
  font-weight: bold;
}
</style>
