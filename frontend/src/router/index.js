// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Waiting from '@/views/Waiting.vue'
import ForgotPassword from '@/views/ForgotPassword.vue'
import Dashboard from '@/views/Dashboard.vue'
// 管理员页面
import AdminUserManagement from '@/views/AdminUserManagement.vue'
import AdminProductManagement from '@/views/AdminProductManagement.vue'
import AdminAnalytics from '@/views/AdminAnalytics.vue'
import AdminWishManagement from '@/views/AdminWishManagement.vue'
import AdminAppealManagement from '@/views/AdminAppealManagement.vue'

// 学生页面
import ProductBrowse from '@/views/ProductBrowse.vue'
import ProductDetail from '@/views/ProductDetail.vue'
import PublishProduct from '@/views/PublishProduct.vue'
import WishSquare from '@/views/WishSquare.vue'
import PublishWish from '@/views/PublishWish.vue'
import Profile from '@/views/Profile.vue'
import CreditDetail from '@/views/CreditDetail.vue'
import EvaluationAppeal from '@/views/EvaluationAppeal.vue'
import NegativeEvaluations from '@/views/NegativeEvaluations.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/waiting',
    name: 'Waiting',
    component: Waiting
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  // 学生路由
  {
    path: '/products',
    name: 'ProductBrowse',
    component: ProductBrowse
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: ProductDetail
  },
  {
    path: '/publish-product',
    name: 'PublishProduct',
    component: PublishProduct
  },
  {
    path: '/wishlist', // 心愿广场
    name: 'WishSquare',
    component: WishSquare
  },
  {
    path: '/publish-wish', // 发布心愿
    name: 'PublishWish',
    component: PublishWish
  },
  {
    path: '/profile', // 个人中心
    name: 'Profile',
    component: Profile
  },
  {
    path: '/credit-detail', // 信用分详情
    name: 'CreditDetail',
    component: CreditDetail
  },
  {
    path: '/appeal/:id', // 评价申诉
    name: 'EvaluationAppeal',
    component: EvaluationAppeal
  },
  {
    path: '/negative-evaluations', // 负面评价管理
    name: 'NegativeEvaluations',
    component: NegativeEvaluations
  },
  // 管理员路由
  {
    path: '/admin/users',
    name: 'AdminUserManagement',
    component: AdminUserManagement
  },
  {
    path: '/admin/products',
    name: 'AdminProductManagement',
    component: AdminProductManagement
  },
  {
    path: '/admin/analytics',
    name: 'AdminAnalytics',
    component: AdminAnalytics
  },
  {
    path: '/admin/wishes', // 管理员心愿管理
    name: 'AdminWishManagement',
    component: AdminWishManagement
  },
  {
    path: '/admin/appeals', // 管理员申诉管理
    name: 'AdminAppealManagement',
    component: AdminAppealManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

