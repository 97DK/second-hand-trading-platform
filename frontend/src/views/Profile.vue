<!-- frontend/src/views/Profile.vue -->
<template>
  <div class="profile">
    <el-row :gutter="20">
      <!-- 侧边栏 -->
      <el-col :span="6">
        <el-card class="profile-sidebar">
          <div class="user-info">
            <el-avatar
              :src="user.avatar ? 'http://127.0.0.1:8000' + user.avatar : null"
              :size="80"
            >
              {{ user.nickname?.charAt(0) }}
            </el-avatar>
            <h3>{{ user.nickname }}</h3>
            <p class="user-type">{{ getUserTypeLabel(user.user_type) }}</p>
            <!-- 显示余额 -->
            <p class="balance-info" v-if="user.user_type === 'student'">
              余额：<span class="balance-amount">¥{{ user.balance }}</span>
            </p>
            <!-- 显示信用分 -->
            <p class="credit-info" v-if="user.user_type === 'student'">
              我的信用分：<span 
                class="credit-amount" 
                :class="{'perfect-score': user.credit_score === 100, 'low-score': user.credit_score < 80}"
                @click="goToCreditDetail"
                style="cursor: pointer; text-decoration: underline;"
              >
                {{ user.credit_score }}分
              </span>
            </p>
            <!-- 充值和提现按钮 -->
            <div v-if="user.user_type === 'student'" class="balance-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click="showRechargeDialog"
                class="recharge-button"
              >
                充值
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="showWithdrawDialog"
                class="withdraw-button"
              >
                提现
              </el-button>
            </div>
          </div>

          <el-menu
            :default-active="activeMenu"
            class="profile-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="my-products">
              <el-icon><Goods /></el-icon>
              <span>我发布的</span>
            </el-menu-item>
            <el-menu-item index="sold-orders">
              <el-icon><SoldOut /></el-icon>
              <span>我卖出的</span>
            </el-menu-item>
            <el-menu-item index="negative-evaluations">
              <el-icon><Warning /></el-icon>
              <span>负面评价</span>
              <el-badge 
                v-if="negativeEvaluationCount > 0" 
                :value="negativeEvaluationCount" 
                type="danger" 
                class="evaluation-badge" 
              />
            </el-menu-item>
            <el-menu-item index="bought-orders">
              <el-icon><ShoppingCart /></el-icon>
              <span>我买到的</span>
            </el-menu-item>
            <el-menu-item index="chat-history">
              <el-icon><ChatDotRound /></el-icon>
              <span>
                聊天记录
                <el-badge v-if="unreadCount > 0" :value="unreadCount" class="unread-badge" />
              </span>
            </el-menu-item>
            <el-menu-item index="my-wishes">
              <el-icon><Star /></el-icon>
              <span>我的心愿</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 主内容区 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <h2>{{ menuTitles[activeMenu] }}</h2>
          </template>

          <!-- 我发布的商品标签页 -->
          <div v-if="activeMenu === 'my-products'" class="my-products-module">
            <el-tabs v-model="productStatusTab" @tab-change="fetchMyProducts">
              <el-tab-pane label="待审核" name="pending">
                <el-table :data="pendingProducts" style="width: 100%">
                  <el-table-column prop="title" label="商品名称"></el-table-column>
                  <el-table-column prop="price" label="价格"></el-table-column>
                  <el-table-column label="状态">
                    <template #default="{ row }">
                      <el-tag type="warning">待审核</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作">
                    <template #default="{ row }">
                      <el-button size="small" @click="editProduct(row)">编辑</el-button>
                      <el-button size="small" type="danger" @click="deleteProduct(row)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>

              <el-tab-pane label="已上架" name="on_sale">
                <el-table :data="onSaleProducts" style="width: 100%">
                  <el-table-column prop="title" label="商品名称"></el-table-column>
                  <el-table-column prop="price" label="价格"></el-table-column>
                  <el-table-column label="状态">
                    <template #default="{ row }">
                      <el-tag type="success">出售中</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作">
                    <template #default="{ row }">
                      <el-button size="small" @click="editProduct(row)">编辑</el-button>
                      <el-button size="small" type="warning" @click="takeDownProduct(row)">下架</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>

              <el-tab-pane label="已下架" name="removed">
                <el-table :data="removedProducts" style="width: 100%">
                  <el-table-column prop="title" label="商品名称"></el-table-column>
                  <el-table-column prop="price" label="价格"></el-table-column>
                  <el-table-column label="状态">
                    <template #default="{ row }">
                      <el-tag type="info">已下架</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作">
                    <template #default="{ row }">
                      <el-button size="small" @click="editProduct(row)">编辑</el-button>
                      <el-button size="small" type="success" @click="relistProduct(row)">重新上架</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>

              <el-tab-pane label="违规商品" name="rejected">
                <el-table :data="rejectedProducts" style="width: 100%">
                  <el-table-column prop="title" label="商品名称"></el-table-column>
                  <el-table-column prop="price" label="价格"></el-table-column>
                  <el-table-column label="状态">
                    <template #default="{ row }">
                      <el-tag type="danger">被拒绝</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作">
                    <template #default="{ row }">
                      <el-button size="small" @click="viewRejectionReason(row)">查看原因</el-button>
                      <el-button size="small" @click="editProduct(row)">重新提交</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 我卖出的 -->
          <div v-else-if="activeMenu === 'sold-orders'">
            <el-table :data="soldProducts" style="width: 100%">
              <el-table-column prop="title" label="商品名称"></el-table-column>
              <el-table-column prop="price" label="售价"></el-table-column>
              <el-table-column prop="sale_quantity" label="数量">
                <template #default="{ row }">
                  {{ row.sale_quantity }}件
                </template>
              </el-table-column>
              <el-table-column prop="buyer_nickname" label="买家"></el-table-column>
              <el-table-column prop="sold_at" label="成交时间">
                <template #default="{ row }">
                  {{ formatDate(row.sold_at) }}
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="soldProducts.length === 0" description="暂无卖出记录" />
          </div>

          <!-- 我买到的 -->
          <div v-else-if="activeMenu === 'bought-orders'">
            <el-table :data="boughtProducts" style="width: 100%">
              <el-table-column prop="title" label="商品名称"></el-table-column>
              <el-table-column prop="price" label="价格"></el-table-column>
              <el-table-column prop="purchase_quantity" label="数量">
                <template #default="{ row }">
                  {{ row.purchase_quantity }}件
                </template>
              </el-table-column>
              <el-table-column prop="seller_nickname" label="卖家"></el-table-column>
              <el-table-column prop="purchased_at" label="购买时间">
                <template #default="{ row }">
                  {{ formatDate(row.purchased_at) }}
                </template>
              </el-table-column>
              <el-table-column label="评价状态">
                <template #default="{ row }">
                  <div v-if="!row.has_evaluation" style="display: flex; align-items: center; gap: 10px;">
                    <el-tag size="small" type="info">待评价</el-tag>
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="goToEvaluation(row)"
                    >
                      立即评价
                    </el-button>
                  </div>
                  <div v-else>
                    <el-tag size="small" type="success">已评价</el-tag>
                    <el-button 
                      v-if="row.evaluation?.appeal_status === 'pending' && new Date() < new Date(row.evaluation?.appeal_deadline)"
                      size="small" 
                      type="warning" 
                      @click="goToAppeal(row.evaluation?.id)"
                      style="margin-left: 5px;"
                    >
                      申诉
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button size="small" @click="viewProduct(row)">查看商品</el-button>
                  <el-button 
                    v-if="row.has_evaluation" 
                    size="small" 
                    type="primary" 
                    @click="viewEvaluationDetail(row)"
                    style="margin-left: 5px;"
                  >
                    查看评价详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="boughtProducts.length === 0" description="暂无购买记录" />
          </div>

          <!-- 聊天记录 -->
          <div v-else-if="activeMenu === 'chat-history'">
            <el-table :data="chatMessages" style="width: 100%">
              <el-table-column label="联系人">
                <template #default="{ row }">
                  <div class="contact-info">
                    <el-avatar
                      :src="getContactAvatar(row)"
                      size="small"
                    >
                      {{ getContactNickname(row)?.charAt(0) }}
                    </el-avatar>
                    <span class="contact-name">{{ getContactNickname(row) }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="content" label="最新消息">
                <template #default="{ row }">
                  <div class="message-preview">
                    <span :class="{ 'unread-message': !row.is_read }">{{ row.content }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="时间">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="{ row }">
                  <el-button size="small" @click="viewChat(row)">查看对话</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="chatMessages.length === 0" description="暂无聊天记录" />
          </div>

          <!-- 我的心愿 -->
          <div v-else-if="activeMenu === 'my-wishes'">
            <el-table :data="myWishes" style="width: 100%">
              <el-table-column prop="title" label="心愿标题"></el-table-column>
              <el-table-column prop="description" label="描述"></el-table-column>
              <el-table-column prop="max_price" label="预算">
                <template #default="{ row }">
                  ¥{{ row.max_price || '无限制' }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag v-if="row.status === 'pending'" type="warning">待审核</el-tag>
                  <el-tag v-else-if="row.status === 'approved'" type="success">已通过</el-tag>
                  <el-tag v-else-if="row.status === 'rejected'" type="danger">被拒绝</el-tag>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="myWishes.length === 0" description="暂无心愿单" />
          </div>

          <!-- 其他标签页（占位符） -->
          <div v-else>
            <el-empty :description="`${menuTitles[activeMenu]}功能开发中`" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 充值对话框 -->
    <el-dialog v-model="rechargeDialogVisible" title="充值余额" width="30%">
      <el-form>
        <el-form-item label="充值金额">
          <el-input-number 
            v-model="rechargeAmount" 
            :min="0.01" 
            :max="9999" 
            :precision="2" 
            :step="10"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rechargeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="rechargeBalance">确认充值</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 提现对话框 -->
    <el-dialog v-model="withdrawDialogVisible" title="提现余额" width="30%">
      <el-form>
        <el-form-item label="提现金额">
          <el-input-number 
            v-model="withdrawAmount" 
            :min="0.01" 
            :max="user.balance" 
            :precision="2" 
            :step="10"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="withdrawDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="withdrawBalance">确认提现</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 聊天对话框 -->
    <el-dialog v-model="chatDialogVisible" :title="`与 ${currentChatPartner?.nickname} 的对话`" width="50%">
      <div class="chat-window">
        <div class="chat-messages">
          <div 
            v-for="message in currentChatMessages" 
            :key="message.id" 
            :class="['message', message.sender === user.id ? 'sent' : 'received']"
          >
            <div class="message-content">
              {{ message.content }}
              <div class="message-time">{{ formatTime(message.created_at) }}</div>
            </div>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="newMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
          />
          <el-button type="primary" @click="sendMessage" style="margin-top: 10px;">发送</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import {
  Goods,
  SoldOut,
  ShoppingCart,
  ChatDotRound,
  Star,
  Warning,
  Edit
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// 响应式数据
const user = ref({})
const activeMenu = ref('my-products')
const productStatusTab = ref('pending')

// 我发布的商品数据
const pendingProducts = ref([])
const onSaleProducts = ref([])
const removedProducts = ref([])
const rejectedProducts = ref([])

// 我卖出的商品
const soldProducts = ref([])

// 我买到的商品
const boughtProducts = ref([])

// 我的心愿
const myWishes = ref([])

// 负面评价数量
const negativeEvaluationCount = ref(0)

// 聊天相关
const chatMessages = ref([])
const chatDialogVisible = ref(false)
const currentChatPartner = ref(null)
const currentChatMessages = ref([])
const newMessage = ref('')
const unreadCount = ref(0)

// 对话框控制
const rechargeDialogVisible = ref(false)
const withdrawDialogVisible = ref(false)

// 余额管理
const rechargeAmount = ref(0.01)
const withdrawAmount = ref(0.01)

// 菜单标题
const menuTitles = {
  'my-products': '我发布的商品',
  'sold-orders': '我卖出的',
  'negative-evaluations': '负面评价管理',
  'bought-orders': '我买到的',
  'chat-history': '聊天记录',
  'my-wishes': '我的心愿'
}

// 获取用户类型标签
const getUserTypeLabel = (userType) => {
  const types = {
    'student': '学生用户',
    'admin': '管理员'
  }
  return types[userType] || userType
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 格式化时间
const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  activeMenu.value = index
  switch(index) {
    case 'my-products':
      fetchMyProducts()
      break
    case 'sold-orders':
      fetchSoldProducts()
      break
    case 'negative-evaluations':
      router.push('/negative-evaluations')
      break
    case 'bought-orders':
      fetchBoughtProducts()
      break
    case 'chat-history':
      fetchChatMessages()
      fetchUnreadCount()
      break
    case 'my-wishes':
      fetchMyWishes()
      break
  }
}

// 显示充值对话框
const showRechargeDialog = () => {
  rechargeAmount.value = 0.01
  rechargeDialogVisible.value = true
}

// 显示提现对话框
const showWithdrawDialog = () => {
  withdrawAmount.value = 0.01
  withdrawDialogVisible.value = true
}



// 获取我发布的商品
const fetchMyProducts = async () => {
  try {
    const response = await axios.get('/api/products/my-products/', {
      params: { status: productStatusTab.value }
    })
    switch (productStatusTab.value) {
      case 'pending':
        pendingProducts.value = response.data
        break
      case 'on_sale':
        onSaleProducts.value = response.data
        break
      case 'removed':
        removedProducts.value = response.data
        break
      case 'rejected':
        rejectedProducts.value = response.data
        break
    }
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  }
}

// 获取我卖出的商品
const fetchSoldProducts = async () => {
  try {
    const response = await axios.get('/api/products/sold-products/')
    soldProducts.value = response.data
  } catch (error) {
    ElMessage.error('获取卖出记录失败')
  }
}

// 获取我买到的商品
const fetchBoughtProducts = async () => {
  try {
    const response = await axios.get('/api/products/bought-products/')
    boughtProducts.value = response.data
    
    // 获取每个商品的评价信息
    for (let product of boughtProducts.value) {
      try {
        const evalResponse = await axios.get(`/api/products/${product.id}/evaluate/`)
        if (evalResponse.data && evalResponse.data.length > 0) {
          product.has_evaluation = true
          product.evaluation = evalResponse.data[0]
        } else {
          product.has_evaluation = false
        }
      } catch (evalError) {
        // 没有评价或获取失败
        product.has_evaluation = false
      }
    }
  } catch (error) {
    ElMessage.error('获取购买记录失败')
  }
}

// 获取我的心愿
const fetchMyWishes = async () => {
  try {
    const response = await axios.get('/api/products/my-wishes/')
    myWishes.value = response.data
  } catch (error) {
    ElMessage.error('获取心愿单失败')
  }
}

// 获取聊天记录
const fetchChatMessages = async () => {
  try {
    const response = await axios.get('/api/products/chat/messages/')
    chatMessages.value = response.data
  } catch (error) {
    ElMessage.error('获取聊天记录失败')
  }
}

// 获取未读消息数
const fetchUnreadCount = async () => {
  try {
    const response = await axios.get('/api/products/chat/unread/')
    unreadCount.value = response.data.unread_count
  } catch (error) {
    console.error('获取未读消息数失败')
  }
}

// 获取联系人昵称
const getContactNickname = (message) => {
  if (message.sender === user.value.id) {
    return message.receiver_nickname
  } else {
    return message.sender_nickname
  }
}

// 获取联系人头像
const getContactAvatar = (message) => {
  // 这里可以添加头像逻辑，暂时返回null
  return null
}

// 查看对话
const viewChat = async (message) => {
  // 确定聊天对象
  const partnerId = message.sender === user.value.id ? message.receiver : message.sender
  currentChatPartner.value = {
    id: partnerId,
    nickname: getContactNickname(message)
  }
  
  // 获取对话记录
  try {
    const response = await axios.get(`/api/products/chat/conversation/${partnerId}/`)
    currentChatMessages.value = response.data
    chatDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取对话记录失败')
  }
}

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim()) {
    ElMessage.warning('消息内容不能为空')
    return
  }
  
  try {
    const response = await axios.post('/api/products/chat/messages/', {
      receiver: currentChatPartner.value.id,
      content: newMessage.value
    })
    
    currentChatMessages.value.push(response.data)
    newMessage.value = ''
    
    // 重新获取聊天记录和未读数
    fetchChatMessages()
    fetchUnreadCount()
  } catch (error) {
    ElMessage.error('发送消息失败')
  }
}

// 查看商品详情
const viewProduct = (product) => {
  router.push(`/product/${product.id}`)
}

// 跳转到评价页面
const goToEvaluation = (product) => {
  // 直接跳转到商品详情页并打开评价对话框
  router.push({
    path: `/product/${product.id}`,
    hash: '#evaluate'
  })
}

const goToAppeal = (evaluationId) => {
  router.push(`/appeal/${evaluationId}`)
}

// 查看评价详情
const viewEvaluationDetail = async (product) => {
  try {
    // 获取评价详情
    const response = await axios.get(`/api/products/${product.id}/evaluate/`)
    if (response.data && response.data.length > 0) {
      const evaluation = response.data[0]
      ElMessageBox.alert(
        `<div>
          <h4>评价详情</h4>
          <p><strong>是否收到货：</strong>${evaluation.received_item === 'yes' ? '是' : '否'}</p>
          <p><strong>是否与商品描述一致：</strong>${evaluation.description_match === 'yes' ? '是' : '否'}</p>
          <p><strong>商家服务态度：</strong>${evaluation.service_attitude === 'yes' ? '是' : '否'}</p>
          <p><strong>评价时间：</strong>${formatDate(evaluation.created_at)}</p>
        </div>`,
        '评价详情',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '确定'
        }
      )
    }
  } catch (error) {
    ElMessage.error('获取评价详情失败')
  }
}

// 编辑商品
const editProduct = (product) => {
  ElMessage.info('编辑商品功能开发中')
}

// 删除商品
const deleteProduct = (product) => {
  ElMessageBox.confirm('确认删除该商品吗？', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/products/${product.id}/`)
      ElMessage.success('删除成功')
      fetchMyProducts()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 下架商品
const takeDownProduct = (product) => {
  ElMessageBox.confirm('确认下架该商品吗？', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.patch(`/api/products/${product.id}/`, { status: 'removed' })
      ElMessage.success('下架成功')
      fetchMyProducts()
    } catch (error) {
      ElMessage.error('下架失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 重新上架商品
const relistProduct = (product) => {
  ElMessageBox.confirm('确认重新上架该商品吗？', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.patch(`/api/products/${product.id}/`, { status: 'pending' })
      ElMessage.success('重新上架成功，需等待审核')
      fetchMyProducts()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 查看拒绝原因
const viewRejectionReason = (product) => {
  ElMessageBox.alert('商品因不符合平台规范被拒绝', '拒绝原因', {
    confirmButtonText: '知道了'
  })
}

// 充值余额
const rechargeBalance = async () => {
  if (rechargeAmount.value < 0.01 || rechargeAmount.value > 9999) {
    ElMessage.error('充值金额必须在0.01-9999之间')
    return
  }

  try {
    const response = await axios.post('/api/users/recharge/', {
      amount: rechargeAmount.value
    })
    
    // 更新本地余额显示
    user.value.balance = response.data.balance
    authStore.user.balance = response.data.balance
    
    ElMessage.success('充值成功')
    rechargeDialogVisible.value = false
  } catch (error) {
    ElMessage.error('充值失败')
  }
}

// 提现余额
const withdrawBalance = async () => {
  if (withdrawAmount.value < 0.01 || withdrawAmount.value > user.value.balance) {
    ElMessage.error('提现金额无效')
    return
  }

  try {
    const response = await axios.post('/api/users/withdraw/', {
      amount: withdrawAmount.value
    })
    
    // 更新本地余额显示
    user.value.balance = response.data.balance
    authStore.user.balance = response.data.balance
    
    ElMessage.success('提现成功')
    withdrawDialogVisible.value = false
  } catch (error) {
    ElMessage.error('提现失败')
  }
}

// 跳转到信用分详情页面
const goToCreditDetail = () => {
  router.push('/credit-detail')
}

// 获取负面评价数量
const fetchNegativeEvaluationCount = async () => {
  try {
    const response = await axios.get('/api/products/negative-evaluations/')
    negativeEvaluationCount.value = response.data.length
  } catch (error) {
    // 静默失败，不影响主要功能
    console.error('获取负面评价数量失败:', error)
  }
}

// 组件挂载时初始化数据
onMounted(() => {
  console.log('Profile组件已挂载');
  console.log('初始用户信息:', authStore.user);
  // 监听用户信息变化
  user.value = authStore.user
  
  fetchMyProducts()
  fetchNegativeEvaluationCount() // 获取负面评价数量
  // 定期检查未读消息
  fetchUnreadCount()
})

// 监听authStore中的用户信息变化
watch(() => authStore.user, (newUser) => {
  if (newUser) {
    user.value = { ...newUser }
  }
}, { deep: true })

// 组件卸载时清理
onUnmounted(() => {
  // 清理定时器等
})
</script>

<style scoped>
.profile {
  padding: 20px;
}

.profile-sidebar {
  height: 100%;
}

.user-info {
  text-align: center;
  margin-bottom: 30px;
}

.user-info h3 {
  margin: 15px 0 5px 0;
}

.user-type {
  color: #999;
  font-size: 14px;
}

.balance-info {
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.balance-amount {
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
}

.credit-info {
  color: #666;
  font-size: 14px;
  margin-top: 10px;
}

.credit-amount {
  font-weight: bold;
  font-size: 16px;
}

.credit-amount.perfect-score {
  color: #67c23a;
}

.credit-amount.low-score {
  color: #f56c6c;
}

.balance-actions {
  margin-top: 10px;
}

.credit-info {
  margin-bottom: 10px;
}

.profile-menu {
  border: none;
}

/* 确保菜单项内容垂直居中 */
.profile-menu :deep(.el-menu-item) {
  display: flex !important;
  align-items: center !important;
}

/* 确保菜单项内的span内容也垂直居中 */
.profile-menu :deep(.el-menu-item span) {
  display: inline-flex;
  align-items: center;
}

.unread-badge {
  margin-left: 5px;
  vertical-align: middle;
}

.contact-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.contact-name {
  font-weight: bold;
}

.message-preview .unread-message {
  font-weight: bold;
  color: #409eff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.chat-window {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 15px;
}

.message.sent {
  text-align: right;
}

.message.received {
  text-align: left;
}

.message-content {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 4px;
  max-width: 70%;
}

.message.sent .message-content {
  background-color: #409eff;
  color: white;
}

.message.received .message-content {
  background-color: #f0f2f5;
  color: #333;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.chat-input {
  display: flex;
  flex-direction: column;
}

/* 修改导航栏样式 */
.profile-sidebar {
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 5px;
}


/* 修改菜单项文字颜色 */
.profile-menu :deep(.el-menu-item) {
  color: #737BBE;
}

.profile-menu :deep(.el-menu-item:hover) {
  color: #6269a9;
}

.profile-menu :deep(.el-menu-item.is-active) {
  color: #6269a9;
}

/* 修改主内容区卡片样式 */
.el-card {
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 5px;
}

/* 充值按钮样式：紫色背景白色文字 */
.recharge-button {
  background-color: #737BBE !important;
  border-color: #737BBE !important;
  color: white !important;
}

/* 提现按钮样式：白色背景紫色文字和边框 */
.withdraw-button {
  background-color: white !important;
  border-color: #737BBE !important;
  color: #737BBE !important;
}

/* 修改表格标签文字颜色 */
.el-table :deep(.el-table-column__label) {
  color: #737BBE;
}

/* 修改表单标签文字颜色 */
.el-form-item :deep(.el-form-item__label) {
  color: #737BBE;
}

/* 我发布的商品模块特定样式 */
.my-products-module :deep(.el-tabs__item) {
  color: #737BBE;
}

.my-products-module :deep(.el-tabs__item.is-active) {
  color: #737BBE;
  font-weight: bold;
}

.my-products-module :deep(.el-tabs__active-bar) {
  background-color: #737BBE;
}

.my-products-module :deep(.el-button) {
  color: #737BBE;
  border-color: #737BBE;
}

.my-products-module :deep(.el-button:hover) {
  background-color: #f5f5ff;
  border-color: #6269a9;
  color: #6269a9;
}

/* 负面评价徽章样式 */
.evaluation-badge {
  margin-left: 8px;
}

.evaluation-badge :deep(.el-badge__content) {
  background-color: #f56c6c;
  border: none;
}

</style>