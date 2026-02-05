<template>
  <div class="users-container">
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
            <el-form-item label="用户类型">
              <el-select v-model="searchForm.user_type" placeholder="全部" clearable style="width: 100%">
                <el-option label="管理员" :value="1" />
                <el-option label="普通用户" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100%">
                <el-option label="启用" :value="1" />
                <el-option label="禁用" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- 操作按钮（仅管理员可见） -->
      <div v-if="authStore.isAdmin" class="action-bar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>

      <!-- 用户表格 -->
      <el-table
        :data="tableData"
        border
        stripe
        class="user-table"
        v-loading="loading"
      >
        <el-table-column prop="id" label="ID" min-width="80" />
        <el-table-column prop="username" label="用户名" min-width="150" />
        <el-table-column prop="user_type" label="用户类型" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="row.user_type === 1" type="danger">管理员</el-tag>
            <el-tag v-else type="primary">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 1" type="success">启用</el-tag>
            <el-tag v-else type="info">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column v-if="authStore.isAdmin" label="操作" min-width="210">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleToggleStatus(row)">
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
          @current-change="fetchUsers"
          @size-change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="用户名"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="密码"
            show-password
          />
          <span class="form-tip">编辑时留空表示不修改密码</span>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="用户类型" prop="user_type">
          <el-radio-group v-model="userForm.user_type">
            <el-radio :label="0">普通用户</el-radio>
            <el-radio :label="1">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 用户管理页面组件
 * 包含用户列表、搜索、新增、编辑、删除等功能
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()

// 加载状态和表格数据
const loading = ref(false)
const tableData = ref([])

// 搜索表单数据
const searchForm = reactive({
  username: '',
  user_type: null,
  status: null
})

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 对话框状态
const dialogVisible = ref(false)
const dialogTitle = computed(() => isEdit.value ? '编辑用户' : '新增用户')
const isEdit = ref(false)
const submitLoading = ref(false)
const currentUserId = ref(null)

// 用户表单
const userFormRef = ref(null)
const userForm = reactive({
  username: '',
  password: '',
  user_type: 0
})

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 1, max: 50, message: '用户名长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && !value) {
          callback(new Error('请输入密码'))
        } else if (value && value.length < 6) {
          callback(new Error('密码长度至少 6 个字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  user_type: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ]
}

/**
 * 获取用户列表
 */
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    }
    const response = await userApi.getUsers(params)
    tableData.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('获取用户列表错误:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 搜索
 */
const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

/**
 * 重置搜索
 */
const handleReset = () => {
  searchForm.username = ''
  searchForm.user_type = null
  searchForm.status = null
  handleSearch()
}

/**
 * 新增用户
 */
const handleAdd = () => {
  isEdit.value = false
  currentUserId.value = null
  Object.assign(userForm, {
    username: '',
    password: '',
    user_type: 0
  })
  dialogVisible.value = true
}

/**
 * 编辑用户
 */
const handleEdit = (row) => {
  isEdit.value = true
  currentUserId.value = row.id
  Object.assign(userForm, {
    username: row.username,
    password: '',
    user_type: row.user_type
  })
  dialogVisible.value = true
}

/**
 * 提交表单
 */
const handleSubmit = async () => {
  await userFormRef.value?.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          // 编辑模式：只更新密码
          const data = {}
          if (userForm.password) {
            data.password = userForm.password
          }
          await userApi.updateUser(currentUserId.value, data)
          ElMessage.success('用户更新成功')
        } else {
          // 新增模式：创建用户
          await userApi.createUser(userForm)
          ElMessage.success('用户创建成功')
        }
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        console.error('提交错误:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

/**
 * 切换用户状态
 */
const handleToggleStatus = async (row) => {
  const action = row.status === 1 ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const newStatus = row.status === 1 ? 0 : 1
    await userApi.updateUser(row.id, { status: newStatus })
    ElMessage.success(`用户已${action}`)
    fetchUsers()
  } catch {
    // 用户取消操作
  }
}

/**
 * 删除用户
 */
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？此操作不可撤销。`,
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await userApi.deleteUser(row.id)
    ElMessage.success('用户删除成功')
    // 如果当前页只有一条数据且不是第一页，则跳到上一页
    if (tableData.value.length === 1 && pagination.page > 1) {
      pagination.page--
    }
    fetchUsers()
  } catch {
    // 用户取消操作
  }
}

/**
 * 格式化日期时间
 */
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时获取用户列表
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-container {
  width: 100%;
  height: 100%;
}

.content-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-form {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.action-bar {
  margin-bottom: 20px;
}

/* 用户表格：自适应宽度 */
.user-table {
  flex: 1;
  margin-bottom: 20px;
}

/* 表格列宽度设置：使用 min-width 让列自适应 */
.user-table :deep(.el-table__body-wrapper) {
  flex: 1;
}

/* 分页器容器 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 10px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}
</style>
