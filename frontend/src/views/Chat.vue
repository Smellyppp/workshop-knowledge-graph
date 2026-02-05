<template>
  <div class="chat-container">
    <el-card shadow="never" class="chat-card">
      <template #header>
        <div class="chat-header">
          <div class="header-left">
            <el-icon :size="24" color="#409EFF">
              <ChatDotRound />
            </el-icon>
            <span class="header-title">智能故障诊断助手</span>
          </div>
          <div class="header-right">
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleClearHistory"
              :disabled="messages.length === 0"
            >
              清除对话
            </el-button>
          </div>
        </div>
      </template>

      <!-- 消息列表区域 -->
      <div class="messages-wrapper" ref="messagesContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <el-empty description="你好！我是车间故障诊断助手">
            <template #image>
              <el-icon :size="80" color="#409EFF">
                <ChatDotRound />
              </el-icon>
            </template>
            <p class="welcome-text">请描述你遇到的设备故障问题，我会尽力帮助你诊断和解决</p>
            <div class="quick-questions">
              <p class="quick-title">试试问我：</p>
              <el-button
                v-for="(question, index) in quickQuestions"
                :key="index"
                type="primary"
                plain
                size="small"
                @click="sendQuickQuestion(question)"
                class="quick-btn"
              >
                {{ question }}
              </el-button>
            </div>
          </el-empty>
        </div>

        <div v-else class="messages-list">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', message.role]"
          >
            <div class="message-content">
              <div class="message-avatar">
                <el-avatar :size="36" :style="getAvatarStyle(message.role)">
                  <el-icon v-if="message.role === 'user'">
                    <User />
                  </el-icon>
                  <el-icon v-else>
                    <Service />
                  </el-icon>
                </el-avatar>
              </div>
              <div class="message-text">
                <div class="message-role">
                  {{ message.role === 'user' ? '我' : 'AI助手' }}
                </div>
                <div class="message-body">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="loading" class="message-item assistant">
            <div class="message-content">
              <div class="message-avatar">
                <el-avatar :size="36" style="background-color: #409EFF">
                  <el-icon>
                    <Service />
                  </el-icon>
                </el-avatar>
              </div>
              <div class="message-text">
                <div class="message-body loading">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-wrapper">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          placeholder="请描述你遇到的故障问题..."
          :disabled="loading"
          @keydown.enter.prevent="handleEnter"
          maxlength="500"
          show-word-limit
          class="message-input"
        />
        <el-button
          type="primary"
          :icon="Promotion"
          @click="handleSend"
          :loading="loading"
          :disabled="!inputMessage.trim()"
          class="send-button"
        >
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound,
  Delete,
  User,
  Service,
  Promotion
} from '@element-plus/icons-vue'
import { sendMessage, clearHistory } from '@/api/chat'

// 状态管理
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const sessionId = ref(generateSessionId())

// 快捷问题列表
const quickQuestions = [
  '设备突然停止运转怎么办？',
  '如何预防设备故障？',
  '设备出现异响是什么原因？'
]

/**
 * 生成会话ID
 */
function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

/**
 * 获取头像样式
 */
function getAvatarStyle(role) {
  return role === 'user'
    ? { backgroundColor: '#67C23A' }
    : { backgroundColor: '#409EFF' }
}

/**
 * 发送快捷问题
 */
async function sendQuickQuestion(question) {
  inputMessage.value = question
  await handleSend()
}

/**
 * 处理Enter键发送
 */
function handleEnter(event) {
  // Shift+Enter 换行，Enter 发送
  if (!event.shiftKey) {
    handleSend()
  }
}

/**
 * 发送消息
 */
async function handleSend() {
  const message = inputMessage.value.trim()
  if (!message || loading.value) {
    return
  }

  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: message,
    time: formatTime(new Date())
  }
  messages.value.push(userMessage)

  // 清空输入框
  inputMessage.value = ''
  loading.value = true

  // 滚动到底部
  await scrollToBottom()

  try {
    // 调用API
    const response = await sendMessage({
      message: message,
      session_id: sessionId.value
    })

    // 添加AI回复
    const assistantMessage = {
      role: 'assistant',
      content: response.message,
      time: formatTime(new Date())
    }
    messages.value.push(assistantMessage)

    // 滚动到底部
    await scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error(error.response?.data?.detail || '发送失败，请稍后重试')

    // 移除用户消息（如果发送失败）
    messages.value.pop()
  } finally {
    loading.value = false
  }
}

/**
 * 清除对话历史
 */
async function handleClearHistory() {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有对话记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await clearHistory(sessionId.value)

    // 清空消息列表
    messages.value = []

    // 生成新的会话ID
    sessionId.value = generateSessionId()

    ElMessage.success('对话历史已清除')
  } catch (error) {
    // 用户取消操作
  }
}

/**
 * 滚动到底部
 */
async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

/**
 * 格式化时间
 */
function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-card :deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #EBEEF5;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #F5F7FA;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
}

.welcome-text {
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
  text-align: center;
}

.quick-questions {
  margin-top: 30px;
  text-align: center;
}

.quick-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 15px;
}

.quick-btn {
  margin: 5px;
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
}

.message-item {
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-content {
  display: flex;
  gap: 12px;
}

.message-item.user .message-content {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-text {
  max-width: 70%;
}

.message-role {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.message-item.user .message-role {
  text-align: right;
}

.message-body {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-item.user .message-body {
  background-color: #67C23A;
  color: white;
}

.message-item.assistant .message-body {
  background-color: white;
  color: #303133;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-time {
  font-size: 11px;
  color: #C0C4CC;
  margin-top: 4px;
}

.message-item.user .message-time {
  text-align: right;
}

/* 加载动画 */
.message-body.loading {
  background-color: white;
  padding: 16px 20px;
  display: flex;
  gap: 4px;
  align-items: center;
}

.dot {
  width: 8px;
  height: 8px;
  background-color: #409EFF;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 输入区域 */
.input-wrapper {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background-color: white;
  border-top: 1px solid #EBEEF5;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 8px;
}

.send-button {
  height: auto;
  min-height: 54px;
  padding: 0 30px;
}

/* 滚动条样式 */
.messages-wrapper::-webkit-scrollbar {
  width: 6px;
}

.messages-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.messages-wrapper::-webkit-scrollbar-thumb {
  background: #DCDFE6;
  border-radius: 3px;
}

.messages-wrapper::-webkit-scrollbar-thumb:hover {
  background: #C0C4CC;
}
</style>
