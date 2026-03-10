<template>
  <div class="graph-container">
    <div ref="graphContainer" class="graph-canvas"></div>

    <!-- 右侧节点详情面板 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="节点详情"
      direction="rtl"
      size="400px"
    >
      <div v-if="selectedNode" class="node-detail">
        <!-- 节点类型标签 -->
        <el-tag v-for="label in selectedNode.labels" :key="label" class="node-label" size="large">
          {{ label }}
        </el-tag>

        <!-- 节点属性 -->
        <el-divider />
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(value, key) in displayProperties"
            :key="key"
            :label="key"
          >
            {{ formatValue(value) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>

    <!-- 控制按钮组 -->
    <div class="graph-controls">
      <el-button-group size="small">
        <el-button @click="fitView">
          <el-icon><FullScreen /></el-icon>
          适配视图
        </el-button>
        <el-button @click="zoomIn">
          <el-icon><ZoomIn /></el-icon>
          放大
        </el-button>
        <el-button @click="zoomOut">
          <el-icon><ZoomOut /></el-icon>
          缩小
        </el-button>
      </el-button-group>
      <div class="graph-stats">
        节点: {{ nodeCount }} | 关系: {{ edgeCount }}
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Neo4j 图谱可视化组件
 * 使用 vis-network 展示节点和关系
 */
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import { Network } from 'vis-network/standalone'
import 'vis-network/styles/vis-network.css'

const props = defineProps({
  nodes: {
    type: Array,
    default: () => []
  },
  edges: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['node-click', 'node-double-click'])

const graphContainer = ref(null)
let network = null
const nodeCount = ref(0)
const edgeCount = ref(0)

// 详情面板
const detailDrawerVisible = ref(false)
const selectedNode = ref(null)

// 计算显示的属性（过滤掉空值和内部字段）
const displayProperties = computed(() => {
  if (!selectedNode.value || !selectedNode.value.properties) {
    return {}
  }

  const props = {}
  const properties = selectedNode.value.properties

  // 字段显示名称映射
  const fieldNames = {
    '设备编号': '设备编号',
    '设备名称': '设备名称',
    '设备型号': '设备型号',
    '设备类型': '设备类型',
    '所在工位': '所在工位',
    '故障率': '故障率',
    '工号': '工号',
    '姓名': '姓名',
    '人员类型': '人员类型',
    '技能等级': '技能等级',
    '工艺编号': '工艺编号',
    '工艺名称': '工艺名称',
    '工艺类型': '工艺类型',
    '物料编号': '物料编号',
    '物料名称': '物料名称',
    '物料类型': '物料类型',
    '故障编号': '故障编号',
    '故障名称': '故障名称',
    '故障现象': '故障现象',
    '故障原因': '故障原因'
  }

  for (const [key, value] of Object.entries(properties)) {
    // 只显示有值的字段
    if (value !== null && value !== undefined && value !== '') {
      props[fieldNames[key] || key] = value
    }
  }

  return props
})

// 格式化属性值
const formatValue = (value) => {
  if (typeof value === 'number') {
    // 检查是否是故障率（0-1之间的小数）
    if (value < 1 && value > 0) {
      return (value * 100).toFixed(2) + '%'
    }
  }
  return String(value)
}

// 车间数据类型颜色映射
const colorMap = {
  '设备': '#3498db',           // 蓝色
  '人员': '#2ecc71',           // 绿色
  '工艺': '#e67e22',           // 橙色
  '物料': '#f1c40f',           // 黄色
  '故障': '#e74c3c',           // 红色
  '加工设备': '#3498db',        // 设备-蓝色
  '检测设备': '#5dade2',        // 浅蓝
  '物流设备': '#85c1e9',        // 更浅蓝
  '辅助设备': '#aed6f1',        // 极浅蓝
  '操作人员': '#2ecc71',        // 绿色
  '技术人员': '#27ae60',        // 深绿
  '管理人员': '#16a085',        // 青绿
  '原材料': '#f1c40f',          // 黄色
  '半成品': '#f39c12',          // 橙黄
  '成品': '#e67e22',            // 深橙
  '辅料': '#d35400',            // 焦橙
  '加工工艺': '#e67e22',        // 橙色
  '检测工艺': '#d35400',        // 深橙
  '装配工艺': '#ca6f1e',        // 更深橙
  'default': '#95a5a6'         // 默认灰色
}

// 获取节点显示名称
const getNodeLabel = (node) => {
  const properties = node.properties || {}
  const labels = node.labels || []

  // 按优先级获取显示名称
  const displayFields = [
    '设备名称', '姓名', '工艺名称', '物料名称', '故障名称',
    '设备编号', '工号', '工艺编号', '物料编号', '故障编号',
    'title', 'name'
  ]

  for (const field of displayFields) {
    if (properties[field]) {
      return String(properties[field])
    }
  }

  // 使用标签作为后备
  return labels[0] || '节点'
}

// 获取节点主类型（用于颜色）
const getMainType = (node) => {
  const labels = node.labels || []

  // 优先级：具体类型 > 通用类型
  const typePriority = [
    '加工设备', '检测设备', '物流设备', '辅助设备',
    '操作人员', '技术人员', '管理人员',
    '原材料', '半成品', '成品', '辅料',
    '加工工艺', '检测工艺', '装配工艺',
    '设备', '人员', '工艺', '物料', '故障'
  ]

  for (const type of typePriority) {
    if (labels.includes(type)) {
      return type
    }
  }

  return labels[0] || 'default'
}

// 节点样式配置
const getNodeOptions = (node) => {
  if (!node) return null

  const mainType = getMainType(node)
  const label = getNodeLabel(node)

  return {
    id: node.id,
    label: label,
    title: `点击查看详情`, // 鼠标悬停提示
    color: colorMap[mainType] || colorMap.default,
    font: {
      size: 14,
      color: '#2c3e50'
    },
    borderWidth: 2,
    borderWidthSelected: 3,
    shape: 'box',
    margin: 10,
    shadow: {
      enabled: true,
      color: 'rgba(0,0,0,0.15)',
      size: 4,
      x: 2,
      y: 2
    }
  }
}

// 关系样式配置
const getEdgeOptions = (edge) => {
  if (!edge || !edge.from_node || !edge.to_node) return null

  return {
    id: edge.id || `${edge.from_node}-${edge.to_node}`,
    from: edge.from_node,
    to: edge.to_node,
    label: edge.type || '',
    arrows: 'to',
    color: {
      color: '#bdc3c7',
      highlight: '#3498db',
      hover: '#3498db'
    },
    font: {
      size: 11,
      align: 'middle',
      background: 'white',
      color: '#7f8c8d'
    },
    smooth: {
      type: 'curvedCW',
      roundness: 0.2
    }
  }
}

// 初始化图谱
const initGraph = () => {
  if (!graphContainer.value) return

  const visNodes = props.nodes
    .map(getNodeOptions)
    .filter(node => node !== null)

  const visEdges = props.edges
    .map(getEdgeOptions)
    .filter(edge => edge !== null)

  nodeCount.value = visNodes.length
  edgeCount.value = visEdges.length

  const data = {
    nodes: visNodes,
    edges: visEdges
  }

  const options = {
    nodes: {
      shape: 'box',
      margin: 10,
      widthConstraint: {
        maximum: 150
      },
      font: {
        size: 14
      }
    },
    edges: {
      width: 2,
      selectionWidth: 3
    },
    physics: {
      enabled: true,
      barnesHut: {
        gravitationalConstant: -3000,
        centralGravity: 0.3,
        springLength: 150,
        springConstant: 0.04,
        damping: 0.09,
        avoidOverlap: 0.5
      },
      stabilization: {
        iterations: 200
      }
    },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      zoomView: true,
      dragView: true,
      navigationButtons: false
    },
    layout: {
      improvedLayout: true,
      hierarchical: {
        enabled: false,
        direction: 'UD',
        sortMethod: 'directed'
      }
    }
  }

  network = new Network(graphContainer.value, data, options)

  // 监听稳定化完成事件
  network.on('stabilizationIterationsDone', () => {
    network.setOptions({
      physics: {
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.1,
          springLength: 150,
          springConstant: 0.05,
          damping: 0.2
        }
      }
    })
  })

  // 点击节点事件 - 显示详情
  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = props.nodes.find(n => n.id === nodeId)

      network.selectNodes([nodeId])

      // 设置选中的节点并显示详情面板
      selectedNode.value = node
      detailDrawerVisible.value = true

      // 同时发出事件给父组件
      emit('node-click', { nodeId, node })
    } else {
      // 点击空白处关闭详情面板
      detailDrawerVisible.value = false
    }
  })

  // 双击节点事件 - 适配视图
  network.on('doubleClick', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      network.fit({
        nodes: [nodeId],
        animation: {
          duration: 500,
          easingFunction: 'easeInOutQuad'
        }
      })

      const node = props.nodes.find(n => n.id === nodeId)
      emit('node-double-click', { nodeId, node })
    }
  })

  // 悬停节点事件 - 高亮边
  network.on('hoverNode', (params) => {
    const nodeId = params.node
    network.selectNodes([nodeId])
  })

  network.on('blurNode', () => {
    network.unselectAllNodes()
  })
}

// 更新图谱数据
const updateGraph = () => {
  if (!network) return

  const visNodes = props.nodes
    .map(getNodeOptions)
    .filter(node => node !== null)

  const visEdges = props.edges
    .map(getEdgeOptions)
    .filter(edge => edge !== null)

  nodeCount.value = visNodes.length
  edgeCount.value = visEdges.length

  network.setData({
    nodes: visNodes,
    edges: visEdges
  })

  triggerAnimation()
}

// 触发流动动画效果
const triggerAnimation = () => {
  if (!network) return

  network.setOptions({
    physics: {
      barnesHut: {
        gravitationalConstant: -5000,
        centralGravity: 0.5,
        springLength: 120,
        springConstant: 0.08,
        damping: 0.05
      },
      stabilization: {
        iterations: 300,
        updateInterval: 25
      }
    }
  })

  network.stabilize()
}

// 适配视图
const fitView = () => {
  if (network) {
    network.fit({
      animation: {
        duration: 500,
        easingFunction: 'easeInOutQuad'
      }
    })
  }
}

// 放大
const zoomIn = () => {
  if (network) {
    network.moveTo({
      scale: network.getScale() * 1.2,
      animation: true
    })
  }
}

// 缩小
const zoomOut = () => {
  if (network) {
    network.moveTo({
      scale: network.getScale() * 0.8,
      animation: true
    })
  }
}

// 监听数据变化
watch(() => [props.nodes, props.edges], () => {
  updateGraph()
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initGraph()
  })
})

onBeforeUnmount(() => {
  if (network) {
    network.destroy()
    network = null
  }
})

defineExpose({
  fitView,
  zoomIn,
  zoomOut,
  triggerAnimation
})
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.graph-canvas {
  width: 100%;
  height: calc(100% - 40px);
  background: #f8f9fa;
  border-radius: 4px;
}

.graph-controls {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.graph-stats {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

/* 节点详情样式 */
.node-detail {
  padding: 20px;
}

.node-label {
  margin-right: 8px;
  margin-bottom: 8px;
}

.node-detail :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #303133;
}
</style>
