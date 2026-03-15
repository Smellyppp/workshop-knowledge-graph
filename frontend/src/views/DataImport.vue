<template>
  <div class="data-import-container">
    <!-- 顶部状态卡片 -->
    <el-card shadow="never" class="status-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="16">
          <div class="status-content">
            <el-icon class="status-icon" :class="healthStatus.status === 'healthy' ? 'success' : 'error'">
              <CircleCheck v-if="healthStatus.status === 'healthy'" />
              <CircleClose v-else />
            </el-icon>
            <span class="status-text">
              数据导入模块状态：
              <el-tag :type="healthStatus.status === 'healthy' ? 'success' : 'danger'">
                {{ healthStatus.status === 'healthy' ? '正常' : '异常' }}
              </el-tag>
              <span v-if="healthStatus.data_directory" class="stats-text">
                | 数据目录: {{ healthStatus.data_directory }}
              </span>
            </span>
          </div>
        </el-col>
        <el-col :span="8">
          <el-button @click="checkHealth" :loading="checking" size="small">
            <el-icon><Refresh /></el-icon>
            检查状态
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 主内容区域 -->
    <el-row :gutter="20">
      <!-- 左侧：文件上传和导入 -->
      <el-col :span="14">
        <el-card shadow="never" class="upload-card">
          <template #header>
            <div class="card-header">
              <el-icon><Upload /></el-icon>
              <span>Excel 数据导入（清空重建）</span>
            </div>
          </template>

          <!-- 上传区域 -->
          <el-upload
            ref="uploadRef"
            class="upload-area"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept=".xlsx,.xls"
            :disabled="importing"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p>拖拽 Excel 文件到此处，或点击选择</p>
              <p class="upload-hint">支持 .xlsx、.xls 格式，文件大小不超过 50MB</p>
            </div>
          </el-upload>

          <!-- 选中的文件信息 -->
          <div v-if="selectedFile" class="selected-file">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              :icon="FolderOpened"
              @click="selectFile"
              :disabled="importing"
              size="large"
            >
              选择文件
            </el-button>
            <input
              ref="fileInputRef"
              type="file"
              accept=".xlsx,.xls"
              style="display: none"
              @change="handleFileSelect"
            />

            <el-button
              type="danger"
              :icon="RefreshRight"
              @click="handleClearAndImport"
              :disabled="!selectedFile || importing"
              :loading="importing"
              size="large"
            >
              清空并导入
            </el-button>
          </div>

          <!-- 导入进度 -->
          <div v-if="importing" class="progress-area">
            <el-alert
              type="warning"
              :closable="false"
              show-icon
              style="margin-bottom: 15px"
            >
              <strong>警告：</strong>导入过程将清空现有的知识图谱数据并重新构建，请谨慎操作！
            </el-alert>
            <el-progress :percentage="importProgress" :indeterminate="true" :status="importSuccess === false ? 'exception' : undefined" />
            <p class="progress-text">
              {{ importMessage || '正在导入数据到 Neo4j...' }}
            </p>
          </div>
        </el-card>

        <!-- 导入结果卡片 -->
        <el-card v-if="importResult" shadow="never" class="result-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>导入结果</span>
              <el-tag :type="importResult.success ? 'success' : 'danger'" style="margin-left: 10px">
                {{ importResult.success ? '成功' : '失败' }}
              </el-tag>
            </div>
          </template>

          <!-- 统计信息 -->
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="设备节点">{{ importResult.statistics.device_count }}</el-descriptions-item>
            <el-descriptions-item label="人员节点">{{ importResult.statistics.person_count }}</el-descriptions-item>
            <el-descriptions-item label="物料节点">{{ importResult.statistics.material_count }}</el-descriptions-item>
            <el-descriptions-item label="工艺节点">{{ importResult.statistics.process_count }}</el-descriptions-item>
            <el-descriptions-item label="故障节点">{{ importResult.statistics.fault_count }}</el-descriptions-item>
            <el-descriptions-item label="总节点数">{{ importResult.statistics.total_nodes }}</el-descriptions-item>
            <el-descriptions-item label="关系数量" :span="2">{{ importResult.statistics.relation_count }}</el-descriptions-item>
            <el-descriptions-item label="耗时">{{ importResult.statistics.duration_seconds }} 秒</el-descriptions-item>
          </el-descriptions>

          <!-- 错误信息 -->
          <div v-if="importResult.errors && importResult.errors.length > 0" class="errors-section">
            <el-divider content-position="left">
              错误信息 (共 {{ importResult.errors.length }} 条)
            </el-divider>
            <el-table :data="importResult.errors.slice(0, 10)" max-height="200" size="small">
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column prop="error_type" label="错误类型" width="120" />
              <el-table-column prop="message" label="错误信息" show-overflow-tooltip />
            </el-table>
            <el-alert
              v-if="importResult.errors.length > 10"
              type="info"
              :closable="false"
              style="margin-top: 10px"
            >
              还有 {{ importResult.errors.length - 10 }} 条错误未显示
            </el-alert>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：数据库上传记录 -->
      <el-col :span="10">
        <el-card shadow="never" class="records-card">
          <template #header>
            <div class="card-header">
              <div>
                <el-icon><Folder /></el-icon>
                <span>数据库上传记录</span>
              </div>
              <el-button
                type="primary"
                size="small"
                :icon="Refresh"
                @click="loadUploadRecords"
                :loading="loadingRecords"
              >
                刷新
              </el-button>
            </div>
          </template>

          <el-table :data="recordList" size="small" max-height="500">
            <el-table-column prop="filename" label="文件名" show-overflow-tooltip min-width="150">
              <template #default="{ row }">
                <el-icon><Document /></el-icon>
                {{ row.filename }}
              </template>
            </el-table-column>
            <el-table-column prop="file_size" label="大小" width="80">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag v-if="row.status === 'success'" type="success" size="small">成功</el-tag>
                <el-tag v-else-if="row.status === 'failed'" type="danger" size="small">失败</el-tag>
                <el-tag v-else-if="row.status === 'importing'" type="warning" size="small">导入中</el-tag>
                <el-tag v-else type="info" size="small">待导入</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  :icon="RefreshRight"
                  link
                  :disabled="importing"
                  @click="handleReimportRecord(row)"
                >
                  重新导入
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  link
                  @click="handleDeleteRecord(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="recordList.length === 0" description="暂无上传记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 数据导入页面
 * 支持上传 Excel 文件并导入到 Neo4j 知识图谱
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  UploadFilled,
  FolderOpened,
  RefreshRight,
  Delete,
  Document,
  Folder,
  Refresh,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { dataImportApi } from '@/api/data-import'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 文件相关
const uploadRef = ref(null)
const fileInputRef = ref(null)
const selectedFile = ref(null)
const importing = ref(false)
const importProgress = ref(0)
const importMessage = ref('')
const importSuccess = ref(null)

// 健康状态
const healthStatus = reactive({
  status: 'unknown',
  data_directory: ''
})
const checking = ref(false)

// 上传记录列表
const recordList = ref([])
const loadingRecords = ref(false)

// 导入结果
const importResult = ref(null)

/**
 * 检查模块健康状态
 */
const checkHealth = async () => {
  checking.value = true
  try {
    const response = await dataImportApi.healthCheck()
    Object.assign(healthStatus, response)

    if (response.status === 'healthy') {
      ElMessage.success('数据导入模块运行正常')
    } else {
      ElMessage.warning('数据导入模块状态异常')
    }
  } catch (error) {
    console.error('健康检查失败:', error)
    healthStatus.status = 'error'
    ElMessage.error('健康检查失败')
  } finally {
    checking.value = false
  }
}

/**
 * 选择文件
 */
const selectFile = () => {
  fileInputRef.value.click()
}

/**
 * 处理文件选择（input change）
 */
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (!beforeUpload(file)) {
      return
    }
    selectedFile.value = file
    importResult.value = null
  }
  // 清空 input 以便重复选择同一文件
  event.target.value = ''
}

/**
 * 处理文件选择（upload change）
 */
const handleFileChange = (file) => {
  if (file.raw) {
    if (!beforeUpload(file.raw)) {
      return
    }
    selectedFile.value = file.raw
    importResult.value = null
  }
}

/**
 * 上传前校验
 */
const beforeUpload = (file) => {
  const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
  if (!isExcel) {
    ElMessage.error('仅支持 .xlsx 或 .xls 格式的 Excel 文件')
    return false
  }

  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }

  return true
}

/**
 * 一键清空并导入
 */
const handleClearAndImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  try {
    await ElMessageBox.confirm(
      '此操作将清空现有的知识图谱数据并重新构建，确定要继续吗？',
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    importing.value = true
    importProgress.value = 0
    importMessage.value = '正在上传并导入...'
    importSuccess.value = null
    importResult.value = null

    // 模拟进度
    const progressInterval = setInterval(() => {
      if (importProgress.value < 90) {
        importProgress.value += 10
      }
    }, 1000)

    const response = await dataImportApi.uploadAndImport(selectedFile.value)

    clearInterval(progressInterval)
    importProgress.value = 100
    importSuccess.value = response.success

    if (response.success) {
      importMessage.value = '导入完成！'
      importResult.value = response

      ElMessage.success({
        message: `导入成功！节点: ${response.statistics.total_nodes}, 关系: ${response.statistics.relation_count}`,
        duration: 5000
      })

      // 刷新记录列表
      loadUploadRecords()
    } else {
      importMessage.value = response.message
      importResult.value = response
      ElMessage.error(response.message || '导入失败')

      // 刷新记录列表
      loadUploadRecords()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导入失败:', error)
      importProgress.value = 100
      importSuccess.value = false
      importMessage.value = '导入失败: ' + (error.message || '未知错误')
      ElMessage.error('导入失败')
    }
  } finally {
    importing.value = false
  }
}

/**
 * 加载上传记录
 */
const loadUploadRecords = async () => {
  loadingRecords.value = true
  try {
    const response = await dataImportApi.getUploadRecords()
    recordList.value = response || []
  } catch (error) {
    console.error('加载上传记录失败:', error)
    ElMessage.error('加载上传记录失败')
  } finally {
    loadingRecords.value = false
  }
}

/**
 * 删除记录
 */
const handleDeleteRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除记录 "${record.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await dataImportApi.deleteUploadRecord(record.file_id)
    ElMessage.success('记录已删除')
    loadUploadRecords()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除记录失败:', error)
      ElMessage.error('删除记录失败')
    }
  }
}

/**
 * 重新导入记录
 */
const handleReimportRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      `确定要使用文件 "${record.filename}" 重新导入吗？这将清空现有的知识图谱数据并重新构建。`,
      '确认重新导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    importing.value = true
    importProgress.value = 0
    importMessage.value = '正在重新导入...'
    importSuccess.value = null
    importResult.value = null

    // 模拟进度
    const progressInterval = setInterval(() => {
      if (importProgress.value < 90) {
        importProgress.value += 10
      }
    }, 1000)

    const response = await dataImportApi.reimportFromRecord(record.file_id)

    clearInterval(progressInterval)
    importProgress.value = 100
    importSuccess.value = response.success

    if (response.success) {
      importMessage.value = '重新导入完成！'
      importResult.value = response

      ElMessage.success({
        message: `重新导入成功！节点: ${response.statistics.total_nodes}, 关系: ${response.statistics.relation_count}`,
        duration: 5000
      })

      // 刷新记录列表
      loadUploadRecords()
    } else {
      importMessage.value = response.message
      importResult.value = response
      ElMessage.error(response.message || '重新导入失败')

      // 刷新记录列表
      loadUploadRecords()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新导入失败:', error)
      importProgress.value = 100
      importSuccess.value = false
      importMessage.value = '重新导入失败: ' + (error.message || '未知错误')
      ElMessage.error('重新导入失败')
    }
  } finally {
    importing.value = false
  }
}

/**
 * 格式化文件大小
 */
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 组件挂载时检查状态并加载记录
onMounted(() => {
  checkHealth()
  loadUploadRecords()
})
</script>

<style scoped>
.data-import-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 状态卡片 */
.status-card {
  flex-shrink: 0;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.status-icon {
  font-size: 20px;
}

.status-icon.success {
  color: #67C23A;
}

.status-icon.error {
  color: #F56C6C;
}

.status-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-text {
  color: #606266;
  font-size: 13px;
}

/* 上传卡片 */
.upload-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.upload-area {
  margin-bottom: 20px;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 40px;
}

.upload-icon {
  font-size: 60px;
  color: #409EFF;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

/* 选中的文件 */
.selected-file {
  margin-bottom: 20px;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;  /* 居中对齐 */
  gap: 20px;
  margin: 30px 0;
}

/* 进度区域 */
.progress-area {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.progress-text {
  margin: 10px 0 0 0;
  font-size: 14px;
  color: #606266;
  text-align: center;
}

/* 结果卡片 */
.result-card {
  margin-top: 20px;
}

.errors-section {
  margin-top: 20px;
}

/* 记录卡片 */
.records-card {
  height: fit-content;
}

.records-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.records-card .card-header > div {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
