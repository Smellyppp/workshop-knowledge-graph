<template>
  <div class="layout-container">
    <el-container class="main-container">
      <!-- 左侧侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <!-- 折叠按钮 -->
        <div class="collapse-btn" @click="toggleCollapse">
          <el-icon>
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
        </div>

        <!-- 菜单 -->
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/chat">
            <el-icon><ChatDotRound /></el-icon>
            <template #title>智能问答</template>
          </el-menu-item>
          <el-menu-item index="/knowledge-graph">
            <el-icon><Share /></el-icon>
            <template #title>知识图谱</template>
          </el-menu-item>
          <!-- 操作日志菜单：仅管理员可见 -->
          <el-menu-item v-if="authStore.isAdmin" index="/operation-logs">
            <el-icon><Document /></el-icon>
            <template #title>操作日志</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区域 -->
      <el-container class="content-container">
        <!-- 顶部导航栏 -->
        <el-header>
          <div class="header-content">
            <h1 class="title">{{ pageTitle }}</h1>
            <div class="user-info">
              <el-dropdown>
                <span class="user-name">
                  <el-icon><User /></el-icon>
                  {{ authStore.user?.username }}
                  <el-tag v-if="authStore.isAdmin" type="danger" size="small" style="margin-left: 8px">管理员</el-tag>
                  <el-tag v-else type="primary" size="small" style="margin-left: 8px">普通用户</el-tag>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleLogout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <!-- 主内容区域 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
/**
 * 主布局组件
 * 包含左侧导航菜单和右侧内容区域
 */
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 页面标题：根据路由显示不同的标题
const pageTitle = computed(() => {
  const titleMap = {
    '/users': '用户管理',
    '/chat': '智能问答',
    '/knowledge-graph': '知识图谱',
    '/operation-logs': '操作日志'
  }
  return titleMap[route.path] || '车间资源系统'
})

/**
 * 切换侧边栏折叠状态
 */
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

/**
 * 处理用户退出登录
 */
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await authStore.logout()
    router.push('/login')
  } catch {
    // 用户取消操作
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.main-container {
  min-height: 100vh;
}

/* 侧边栏样式 */
.sidebar {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.collapse-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #bfcbd9;
  font-size: 20px;
  border-bottom: 1px solid #1f2d3d;
}

.collapse-btn:hover {
  color: #fff;
  background: #263445;
}

.sidebar-menu {
  border: none;
  background: #304156;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

/* 内容区域容器 */
.content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.el-header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.title {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
}

.user-name {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.user-name .el-icon {
  margin-right: 5px;
}

/* 主内容区域 */
.main-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
</style>
