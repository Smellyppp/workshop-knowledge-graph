<template>
  <!-- 路由视图出口 -->
  <router-view />
</template>

<script setup>
// 根组件，用于显示路由匹配的组件
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 设置默认字体 */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 应用最小高度为全屏 */
#app {
  min-height: 100vh;
}
</style>
