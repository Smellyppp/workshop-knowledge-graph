<template>
  <div class="graph-container">
    <div ref="graphContainer" class="graph-canvas"></div>
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
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
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

// 定义颜色映射 - 根据数据库中的实际节点类型
const colorMap = {
  'default': '#97C2FC',      // 默认蓝色
  'Errorid': '#FF6B6B',      // 错误ID - 红色
  'Caozuo': '#4ECDC4',       // 操作 - 青绿色
  'Xianxiang': '#FFA07A',    // 现象 - 橙色
  'GuzhangBuwei': '#DDA0DD', // 故障部位 - 紫色
  'Yuanyin': '#F0E68C',      // 原因 - 黄色
  // 'Equipment': '#87CEEB',    // 设备 - 天蓝色
  // 'Process': '#90EE90',      // 工艺 - 浅绿色
  // 'Material': '#FFB6C1',     // 物料 - 粉色
  // 'Parameter': '#FFE4B5'     // 参数 - 杏色
}

// 节点样式配置
const getNodeOptions = (node) => {
  if (!node) return null

  const properties = node.properties || {}
  const labels = node.labels || []
  const label = properties.title || properties.name || `节点${node.id}`
  const mainLabel = labels[0] || 'Node'

  return {
    id: node.id,
    label: String(label),
    title: `${mainLabel}: ${String(label)}`,
    color: colorMap[mainLabel] || colorMap.default,
    font: {
      size: 14,
      color: '#343434'
    },
    borderWidth: 2,
    borderWidthSelected: 4,
    shape: 'box',
    margin: 10,
    shadow: {
      enabled: true,
      color: 'rgba(0,0,0,0.2)',
      size: 5,
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
      color: '#848484',
      highlight: '#4A90E2',
      hover: '#4A90E2'
    },
    font: {
      size: 12,
      align: 'middle',
      background: 'white'
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
        maximum: 200
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
      dragView: true
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
    // 稳定化完成后，降低物理模拟使节点更易点击
    network.setOptions({
      physics: {
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.1,
          springLength: 150,
          springConstant: 0.05,
          damping: 0.2  // 增加阻尼，减少运动
        }
      }
    })
  })

  // 点击节点事件 - 发出事件给父组件处理展开
  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = props.nodes.find(n => n.id === nodeId)
      network.selectNodes([nodeId])
      // 发出节点点击事件
      emit('node-click', { nodeId, node })
    }
  })

  // 双击节点事件 - 适配视图并发出事件
  network.on('doubleClick', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = props.nodes.find(n => n.id === nodeId)
      network.fit({
        nodes: [nodeId],
        animation: {
          duration: 500,
          easingFunction: 'easeInOutQuad'
        }
      })
      // 发出双击事件
      emit('node-double-click', { nodeId, node })
    }
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

  // 触发流动动画效果
  triggerAnimation()
}

// 触发流动动画效果
const triggerAnimation = () => {
  if (!network) return

  // 临时增强物理效果，创造流动感
  network.setOptions({
    physics: {
      barnesHut: {
        gravitationalConstant: -5000,  // 增强引力
        centralGravity: 0.5,           // 增强中心引力
        springLength: 120,             // 缩短弹簧长度
        springConstant: 0.08,          // 增强弹簧系数
        damping: 0.05                  // 降低阻尼，增加运动
      },
      stabilization: {
        iterations: 300,               // 稳定化迭代次数
        updateInterval: 25             // 更新间隔
      }
    }
  })

  // 触发稳定化
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
</style>
