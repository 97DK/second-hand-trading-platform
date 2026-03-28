<template>
  <div class="waiting-container">
    <el-result
      icon="info"
      title="注册成功"
      sub-title="您的账号正在等待管理员审核，请耐心等待">
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">返回登录</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
</script>

<style scoped>
.waiting-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>