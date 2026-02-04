<template>
  <div class="chat-container">
    <el-card shadow="never" class="content-card">
      <div class="chat-placeholder">
        <el-empty description="智能问答功能开发中">
          <el-icon size="100" color="#909399">
            <ChatDotRound />
          </el-icon>
        </el-empty>
        <p class="hint-text">此模块将在后续版本中实现</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 智能问答页面组件（占位）
 * 此页面为占位符，等待后续开发
 */
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
}

.content-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.hint-text {
  margin-top: 20px;
  font-size: 14px;
  color: #909399;
}
</style>
