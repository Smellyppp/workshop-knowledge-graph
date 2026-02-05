/**
 * 操作日志 API 接口
 * 封装所有操作日志相关的 HTTP 请求
 */
import request from './index'

/**
 * 获取操作日志列表
 * @param {Object} params - 查询参数（分页、筛选等）
 * @returns {Promise} 操作日志列表
 */
export const getOperationLogs = (params) => {
  return request.get('/v1/logs', { params })
}

/**
 * 获取操作日志详情
 * @param {number} id - 日志ID
 * @returns {Promise} 操作日志详情
 */
export const getOperationLogById = (id) => {
  return request.get(`/v1/logs/${id}`)
}

/**
 * 获取操作日志统计信息
 * @returns {Promise} 统计信息
 */
export const getLogStatistics = () => {
  return request.get('/v1/logs/statistics/summary')
}

/**
 * 获取最近操作日志
 * @param {number} limit - 返回记录数
 * @returns {Promise} 最近日志列表
 */
export const getRecentLogs = (limit = 10) => {
  return request.get('/v1/logs/recent', { params: { limit } })
}

// 统一导出
export const operationLogApi = {
  getOperationLogs,
  getOperationLogById,
  getLogStatistics,
  getRecentLogs
}

export default operationLogApi
