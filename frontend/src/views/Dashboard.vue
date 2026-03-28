<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard-container">
    <div class="header-content">
      <div></div>
      <h2 class="title-center">佛山大学二手交易平台</h2>
      <div class="user-info">
        <span>欢迎，{{ authStore.user?.nickname }}</span>
        <el-button @click="handleLogout" type="text">退出登录</el-button>
      </div>
    </div>

    <el-container class="main-container">
      <el-aside width="200px">
        <el-menu
          default-active="1"
          class="sidebar-menu">
          <!-- 学生菜单项 -->
          <template v-if="authStore.user?.user_type === 'student'">
            <el-menu-item index="1" @click="handleMenuItemClick('1')">
              <el-icon><icon-menu /></el-icon>
              <span>商品浏览</span>
            </el-menu-item>
            <el-menu-item index="2" @click="handleMenuItemClick('2')">
              <el-icon><plus /></el-icon>
              <span>发布商品</span>
            </el-menu-item>
            <el-menu-item index="3" @click="handleMenuItemClick('3')">
              <el-icon><star /></el-icon>
              <span>心愿广场</span>
            </el-menu-item>
            <el-menu-item index="4" @click="handleMenuItemClick('4')">
              <el-icon><user /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
          </template>

          <!-- 管理员菜单项 -->
          <template v-else-if="authStore.user?.user_type === 'admin'">
            <el-menu-item index="1" @click="handleMenuItemClick('1')">
              <el-icon><user /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="2" @click="handleMenuItemClick('2')">
              <el-icon><icon-menu /></el-icon>
              <span>商品管理</span>
            </el-menu-item>
            <el-menu-item index="3" @click="handleMenuItemClick('3')">
              <el-icon><star /></el-icon>
              <span>心愿管理</span>
            </el-menu-item>
            <el-menu-item index="4" @click="handleMenuItemClick('4')">
              <el-icon><document /></el-icon>
              <span>申诉管理</span>
            </el-menu-item>
            <el-menu-item index="5" @click="handleMenuItemClick('5')">
              <el-icon><data-analysis /></el-icon>
              <span>数据统计与仪表盘</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>

      <el-main>
        <div class="main-content">
          <h3>欢迎使用二手交易平台</h3>
          <p class="welcome-text">
            欢迎来到佛山大学二手交易平台！<br>
            在这里，每一件物品都有机会重获新生，让闲置焕发新的价值。无论你是想寻找需要的物品，还是希望让闲置继续发光，这里都是属于你的共享空间。<br><br>
            你可以通过 "商品浏览" 探索各类在售好物，或许正好能遇见心仪之选；<br>
            也可以通过 "发布商品" 让手中的闲置流转给需要的人，延续它的使命；<br>
            如果你有明确想要但暂未找到的商品，不妨来 "心愿广场" 发布信息，或许很快就能等到回应；<br>
            即使暂时没有目标，也可以常来逛逛，说不定别人正需要被你遗忘在角落的宝贝呢！
          </p>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Menu as IconMenu, Plus, User, DataAnalysis, Star, Document } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 添加菜单项点击处理函数
const handleMenuItemClick = (index) => {
  if (authStore.user?.user_type === 'student') {
    switch(index) {
      case '1':
        // 商品浏览
        router.push('/products')
        break
      case '2':
        // 发布商品
        router.push('/publish-product')
        break
      case '3':
        // 心愿广场
        router.push('/wishlist')
        break
      case '4':
        // 个人中心
        router.push('/profile')
        break
    }
  } else if (authStore.user?.user_type === 'admin') {
    switch(index) {
      case '1':
        // 用户管理
        router.push('/admin/users')
        break
      case '2':
        // 商品管理
        router.push('/admin/products')
        break
      case '3':
        // 心愿管理
        router.push('/admin/wishes')
        break
      case '4':
        // 申诉管理
        router.push('/admin/appeals')
        break
      case '5':
        // 数据统计与仪表盘
        router.push('/admin/analytics')
        break
    }
  }
}

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  background-image: url('../../public/login-bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background-color: rgba(255, 255, 255, 0.5); /* 50% 透明度 */
  padding: 0 20px;
  width: 100%;
  box-sizing: border-box;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 退出登录按钮样式 */
:deep(.user-info .el-button) {
  color: #737BBE;
}

:deep(.user-info .el-button:hover) {
  color: #6269a9;
}

.title-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  color: #737BBE; /* 紫色 */
  margin: 0;
}

.main-container {
  height: calc(100vh - 60px);
  padding: 10px 10px 10px 0;
  box-sizing: border-box;
}

.sidebar-menu {
  height: 100%;
  background-color: rgba(255, 255, 255, 0.5); /* 50% 透明度 */
  border-radius: 5px;
  margin-right: 10px;
}

.sidebar-menu :deep(.el-menu) {
  background-color: transparent;
  border-right: none;
}

.el-main {
  background-color: rgba(255, 255, 255, 0.5); /* 50% 透明度 */
  border-radius: 5px;
  padding: 20px;
  overflow: hidden;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #737BBE;
  background-color: rgba(255, 255, 255, 0.25); /* 25% 透明度 */
}

.sidebar-menu :deep(.el-menu-item:hover) {
  color: #6269a9;
  background-color: rgba(255, 255, 255, 0.3);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  color: #6269a9;
  background-color: rgba(255, 255, 255, 0.4); /* 40% 透明度 */
}

.main-content {
  height: 100%;
  box-sizing: border-box;
}
</style>