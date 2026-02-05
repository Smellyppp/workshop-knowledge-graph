/**
 * 知识图谱 API 服务
 * 封装所有知识图谱相关的接口调用
 */
import request from './index'

/**
 * 健康检查
 */
export const healthCheck = () => {
  return request.get('/v1/knowledge-graph/health')
}

/**
 * 节点搜索（关键词匹配）
 * @param {string} keyword - 搜索关键词
 * @param {number} limit - 最大返回结果数
 */
export const searchNodes = (keyword, limit = 100) => {
  return request.post('/v1/knowledge-graph/search', null, {
    params: { keyword, limit }
  })
}

/**
 * 获取节点关系
 * @param {number} nodeId - 节点ID
 */
export const getNodeRelationships = (nodeId) => {
  return request.get(`/v1/knowledge-graph/node/${nodeId}/relationships`)
}

/**
 * 获取图谱统计信息
 */
export const getStatistics = () => {
  return request.get('/v1/knowledge-graph/statistics')
}

/**
 * 获取图谱数据（节点和关系）用于可视化
 * @param {number} limit - 最大节点数
 */
export const getGraphData = (limit = 100) => {
  return request.get('/v1/knowledge-graph/graph-data', {
    params: { limit }
  })
}

/**
 * 获取节点的邻居（用于节点展开）
 * @param {string} nodeId - 节点的 elementId
 * @param {number} depth - 扩展深度（默认1）
 */
export const getNodeNeighbors = (nodeId, depth = 1) => {
  return request.get(`/v1/knowledge-graph/neighbors/${nodeId}`, {
    params: { depth }
  })
}

/**
 * 执行自定义 Cypher 查询
 * @param {Object} data - 查询参数
 * @param {string} data.query - Cypher 查询语句
 * @param {Object} [data.parameters] - 查询参数
 */
export const executeCypher = (data) => {
  return request.post('/v1/knowledge-graph/cypher', data)
}

// 统一导出
export const knowledgeGraphApi = {
  healthCheck,
  searchNodes,
  getNodeRelationships,
  getStatistics,
  getGraphData,
  getNodeNeighbors,
  executeCypher
}

export default knowledgeGraphApi
