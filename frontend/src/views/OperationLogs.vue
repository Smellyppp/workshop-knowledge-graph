<template>
  <div class="operation-logs-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">总日志数</div>
              <div class="stat-value">{{ statistics.total_logs || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日日志</div>
              <div class="stat-value">{{ statistics.today_logs || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">活跃用户</div>
              <div class="stat-value">{{ Object.keys(statistics.user_stats || {}).length }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C">
              <el-icon><Files /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">操作类型</div>
              <div class="stat-value">{{ Object.keys(statistics.action_type_stats || {}).length }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志列表 -->
    <el-card shadow="never" class="content-card">
      <!-- 搜索表单 -->
      <el-form :model="searchForm" class="search-form">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <el-form-item label="用户名">
              <el-input v-model="searchForm.username" placeholder="用户名" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <el-form-item label="行为类型">
              <el-select v-model="searchForm.action_type" placeholder="全部" clearable style="width: 100%">
                <el-option label="登录" value="LOGIN" />
                <el-option label="登出" value="LOGOUT" />
                <el-option label="查询" value="QUERY" />
                <el-option label="创建" value="CREATE" />
                <el-option label="更新" value="UPDATE" />
                <el-option label="删除" value="DELETE" />
                <el-option label="搜索" value="SEARCH" />
                <el-option label="导出" value="EXPORT" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <el-form-item label="模块">
              <el-select v-model="searchForm.module" placeholder="全部" clearable style="width: 100%">
                <el-option label="认证" value="认证" />
                <el-option label="用户管理" value="用户管理" />
                <el-option label="知识图谱" value="知识图谱" />
                <el-option label="智能问答" value="智能问答" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100%">
                <el-option label="成功" :value="1" />
                <el-option label="失败" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="12" :lg="12">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="handleReset">重置</el-button>
              <el-button @click="fetchStatistics" :loading="statsLoading">
                <el-icon><Refresh /></el-icon>
                刷新统计
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 日志表格 -->
      <el-table
        :data="tableData"
        border
        stripe
        class="log-table"
        v-loading="loading"
      >
        <el-table-column prop="id" label="ID" min-width="80" />
        <el-table-column prop="username" label="操作用户" min-width="120" />
        <el-table-column prop="action_type" label="行为类型" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getActionTypeTagType(row.action_type)">
              {{ getActionTypeLabel(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="操作模块" min-width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.module }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" min-width="140" />
        <el-table-column prop="status" label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="操作时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchLogs"
          @size-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 操作日志页面组件
 * 包含日志统计、搜索、分页等功能
 * 仅管理员可访问
 */
import { ref, reactive, onMounted } from 'vue'
import { operationLogApi } from '@/api/operation-log'
import { ElMessage } from 'element-plus'

// 加载状态和表格数据
const loading = ref(false)
const statsLoading = ref(false)
const tableData = ref([])

// 统计数据
const statistics = ref({
  total_logs: 0,
  today_logs: 0,
  action_type_stats: {},
  module_stats: {},
  user_stats: {}
})

// 搜索表单数据
const searchForm = reactive({
  username: '',
  action_type: null,
  module: null,
  status: null
})

// 日期范围
const dateRange = ref([])

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

/**
 * 获取操作日志列表
 */
const fetchLogs = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    }

    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }

    const response = await operationLogApi.getOperationLogs(params)
    tableData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取日志列表错误:', error)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 获取统计信息
 */
const fetchStatistics = async () => {
  statsLoading.value = true
  try {
    const response = await operationLogApi.getLogStatistics()
    statistics.value = response
  } catch (error) {
    console.error('获取统计信息错误:', error)
    ElMessage.error('获取统计信息失败')
  } finally {
    statsLoading.value = false
  }
}

/**
 * 搜索
 */
const handleSearch = () => {
  pagination.page = 1
  fetchLogs()
}

/**
 * 重置搜索
 */
const handleReset = () => {
  searchForm.username = ''
  searchForm.action_type = null
  searchForm.module = null
  searchForm.status = null
  dateRange.value = []
  handleSearch()
}

/**
 * 格式化日期时间
 */
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

/**
 * 获取行为类型标签颜色
 */
const getActionTypeTagType = (actionType) => {
  const typeMap = {
    'LOGIN': 'success',
    'LOGOUT': 'info',
    'QUERY': 'primary',
    'CREATE': 'success',
    'UPDATE': 'warning',
    'DELETE': 'danger',
    'SEARCH': 'primary',
    'EXPORT': 'warning'
  }
  return typeMap[actionType] || 'info'
}

/**
 * 获取行为类型显示文本
 */
const getActionTypeLabel = (actionType) => {
  const labelMap = {
    'LOGIN': '登录',
    'LOGOUT': '登出',
    'QUERY': '查询',
    'CREATE': '创建',
    'UPDATE': '更新',
    'DELETE': '删除',
    'SEARCH': '搜索',
    'EXPORT': '导出'
  }
  return labelMap[actionType] || actionType
}

// 组件挂载时获取数据
onMounted(() => {
  fetchLogs()
  fetchStatistics()
})
</script>

<style scoped>
.operation-logs-container {
  width: 100%;
  height: 100%;
}

/* 统计卡片行 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

/* 内容卡片 */
.content-card {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.search-form {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* 日志表格 */
.log-table {
  margin-bottom: 20px;
}

/* 分页器容器 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 10px;
}
</style>
