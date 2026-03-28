<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
  height: 100vh;
  background-image: url('../public/login-bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* 解决 ResizeObserver 警告 */
.resize-observer-fix {
  position: relative;
  z-index: 0;
}

/* 全局修复 ResizeObserver 警告 */
[resizeobserver] {
  display: block;
}
</style>