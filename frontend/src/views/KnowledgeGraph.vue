<template>
  <div class="knowledge-graph-container">
    <!-- 连接状态栏 -->
    <el-card shadow="never" class="status-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="18">
          <div class="status-content">
            <el-icon class="status-icon" :class="connectionStatus.connected ? 'success' : 'error'">
              <CircleCheck v-if="connectionStatus.connected" />
              <CircleClose v-else />
            </el-icon>
            <span class="status-text">
              Neo4j 状态：
              <el-tag :type="connectionStatus.connected ? 'success' : 'danger'">
                {{ connectionStatus.connected ? '已连接' : '未连接' }}
              </el-tag>
              <span v-if="connectionStatus.node_count !== null" class="stats-text">
                | 节点数: {{ connectionStatus.node_count }}
              </span>
              <span v-if="connectionStatus.relationship_count !== null" class="stats-text">
                | 关系数: {{ connectionStatus.relationship_count }}
              </span>
            </span>
          </div>
        </el-col>
        <el-col :span="6">
          <el-button @click="checkConnection" :loading="checking" size="small">
            <el-icon><Refresh /></el-icon>
            检查连接
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 顶部工具栏 -->
    <el-card shadow="never" class="toolbar-card">
      <el-row :gutter="20" align="middle">
        <!-- 搜索 -->
        <el-col :span="10">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索 title 字段..."
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch" :loading="searching">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-col>

        <!-- 数据数量控制 -->
        <el-col :span="8">
          <el-select v-model="dataLimit" @change="handleLimitChange" style="width: 100%">
            <el-option label="50 个节点" :value="50" />
            <el-option label="100 个节点" :value="100" />
            <el-option label="200 个节点" :value="200" />
            <el-option label="500 个节点" :value="500" />
          </el-select>
        </el-col>

        <!-- 刷新按钮 -->
        <el-col :span="6">
          <el-button type="primary" @click="loadGraphData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 图谱可视化 -->
    <el-card shadow="never" class="graph-card">
      <GraphVisualization
        v-if="graphData.nodes.length > 0"
        ref="graphRef"
        :nodes="graphData.nodes"
        :edges="graphData.edges"
        @node-click="handleNodeClick"
        @node-double-click="handleNodeDoubleClick"
      />
      <el-empty v-else description="暂无数据，请点击刷新按钮加载图谱数据" />
    </el-card>
  </div>
</template>

<script setup>
/**
 * 知识图谱页面 - 图谱可视化展示
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import GraphVisualization from '@/components/GraphVisualization.vue'
import { knowledgeGraphApi } from '@/api/knowledge-graph'

// 连接状态
const connectionStatus = reactive({
  connected: false,
  node_count: null,
  relationship_count: null
})
const checking = ref(false)

// 搜索
const searchKeyword = ref('')
const searching = ref(false)
const dataLimit = ref(100)

// 图谱数据
const loading = ref(false)
const graphData = reactive({
  nodes: [],
  edges: []
})

// 图谱组件引用
const graphRef = ref(null)

// 记录每个节点展开时添加的节点和边（用于折叠）
const nodeExpansionMap = ref(new Map())

/**
 * 处理节点点击 - 展开或折叠邻居节点
 */
const handleNodeClick = async ({ nodeId, node }) => {
  console.log('点击节点:', nodeId, node)

  // 检查该节点是否已经展开过
  if (nodeExpansionMap.value.has(nodeId)) {
    // 已展开过，执行折叠操作
    collapseNode(nodeId)
  } else {
    // 未展开过，执行展开操作
    await expandNode(nodeId)
  }
}

/**
 * 展开节点 - 添加邻居节点
 */
const expandNode = async (nodeId) => {
  try {
    const response = await knowledgeGraphApi.getNodeNeighbors(nodeId, 1)
    const neighborNodes = response.nodes || []
    const neighborEdges = response.edges || []

    if (neighborNodes.length === 0) {
      ElMessage.info('该节点没有邻居节点')
      return
    }

    // 记录新添加的节点ID和边ID
    const newNodeIds = []
    const newEdgeIds = []

    // 合并新节点和边
    neighborNodes.forEach(node => {
      if (!graphData.nodes.some(n => n.id === node.id)) {
        graphData.nodes.push(node)
        newNodeIds.push(node.id)
      }
    })

    neighborEdges.forEach(edge => {
      if (!graphData.edges.some(e => e.id === edge.id)) {
        graphData.edges.push(edge)
        newEdgeIds.push(edge.id)
      }
    })

    // 记录该节点展开的数据
    nodeExpansionMap.value.set(nodeId, {
      nodeIds: newNodeIds,
      edgeIds: newEdgeIds
    })

    ElMessage.success(`展开成功：新增 ${newNodeIds.length} 个节点，${newEdgeIds.length} 条关系`)

  } catch (error) {
    console.error('获取节点邻居失败:', error)
    ElMessage.error('展开节点失败')
  }
}

/**
 * 折叠节点 - 移除之前添加的邻居节点
 */
const collapseNode = (nodeId) => {
  const expansionData = nodeExpansionMap.value.get(nodeId)
  if (!expansionData) return

  const { nodeIds, edgeIds } = expansionData

  // 移除节点
  graphData.nodes = graphData.nodes.filter(node => !nodeIds.includes(node.id))

  // 移除边
  graphData.edges = graphData.edges.filter(edge => !edgeIds.includes(edge.id))

  // 移除展开记录
  nodeExpansionMap.value.delete(nodeId)

  ElMessage.info(`折叠节点：移除 ${nodeIds.length} 个节点，${edgeIds.length} 条关系`)

  // 递归：检查是否有其他展开的节点依赖被移除的节点
  // 如果有，也需要移除那些展开记录
  cleanupDependentExpansions(nodeIds)
}

/**
 * 清理依赖被移除节点的展开记录
 */
const cleanupDependentExpansions = (removedNodeIds) => {
  const removedIds = new Set(removedNodeIds)

  // 遍历所有展开记录
  for (const [expandedNodeId, expansionData] of nodeExpansionMap.value) {
    const { nodeIds, edgeIds } = expansionData

    // 检查该展开记录中的节点是否有被移除的
    const hasDependency = nodeIds.some(id => removedIds.has(id))

    if (hasDependency) {
      // 移除该展开记录关联的节点和边
      graphData.nodes = graphData.nodes.filter(node => !nodeIds.includes(node.id))
      graphData.edges = graphData.edges.filter(edge => !edgeIds.includes(edge.id))

      // 删除展开记录
      nodeExpansionMap.value.delete(expandedNodeId)
    }
  }
}

/**
 * 处理节点双击 - 仅适配视图
 */
const handleNodeDoubleClick = ({ nodeId, node }) => {
  console.log('双击节点:', nodeId, node)
  // 双击事件由 GraphVisualization 组件内部处理适配视图
}

/**
 * 检查连接状态
 */
const checkConnection = async () => {
  checking.value = true
  try {
    const response = await knowledgeGraphApi.healthCheck()
    Object.assign(connectionStatus, {
      connected: response.neo4j_connected || false,
      node_count: response.details?.node_count,
      relationship_count: response.details?.relationship_count
    })

    if (connectionStatus.connected) {
      ElMessage.success('Neo4j 连接正常')
    } else {
      ElMessage.error('Neo4j 连接失败，请检查数据库')
    }
  } catch (error) {
    console.error('检查连接失败:', error)
    connectionStatus.connected = false
    ElMessage.error('检查连接失败')
  } finally {
    checking.value = false
  }
}

/**
 * 加载图谱数据
 */
const loadGraphData = async () => {
  loading.value = true
  try {
    const response = await knowledgeGraphApi.getGraphData(dataLimit.value)
    graphData.nodes = response.nodes || []
    graphData.edges = response.edges || []

    if (graphData.nodes.length > 0) {
      ElMessage.success(`加载成功：${graphData.nodes.length} 个节点，${graphData.edges.length} 条关系`)
    } else {
      ElMessage.warning('暂无图谱数据，请先在 Neo4j 中创建数据')
    }
  } catch (error) {
    console.error('加载图谱数据失败:', error)
    ElMessage.error('加载图谱数据失败')
    graphData.nodes = []
    graphData.edges = []
  } finally {
    loading.value = false
  }
}

/**
 * 搜索节点
 */
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  searching.value = true

  try {
    const response = await knowledgeGraphApi.searchNodes(searchKeyword.value, dataLimit.value)
    graphData.nodes = response.nodes || []
    graphData.edges = response.edges || []

    // 清空展开记录
    nodeExpansionMap.value.clear()

    if (graphData.nodes.length === 0) {
      ElMessage.info('未找到匹配的结果')
    } else {
      ElMessage.success(`找到 ${graphData.nodes.length} 个节点，${graphData.edges.length} 条关系`)
      ElMessage.info('提示：点击节点展开/折叠，双击节点适配视图')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败')
    graphData.nodes = []
    graphData.edges = []
  } finally {
    searching.value = false
  }
}

/**
 * 数据数量变化
 */
const handleLimitChange = () => {
  loadGraphData()
}

// 组件挂载时先检查连接，然后加载数据
onMounted(() => {
  checkConnection()
})
</script>

<style scoped>
.knowledge-graph-container {
  width: 100%;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

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

.toolbar-card {
  flex-shrink: 0;
}

.graph-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.graph-card :deep(.el-card__body) {
  flex: 1;
  padding: 0;
  height: 100%;
}
</style>
