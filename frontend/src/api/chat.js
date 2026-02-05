/**
 * 智能问答 API 接口
 */
import request from './index'

/**
 * 发送消息给AI助手
 * @param {Object} data - 请求数据
 * @param {string} data.message - 用户消息内容
 * @param {string} data.session_id - 会话ID（可选）
 * @returns {Promise} 返回AI回复
 */
export function sendMessage(data) {
  return request({
    url: '/v1/chat/message',
    method: 'post',
    data,
    timeout: 90000  // AI调用可能需要较长时间，单独设置90秒超时
  })
}

/**
 * 清除对话历史
 * @param {string} session_id - 会话ID（可选）
 * @returns {Promise}
 */
export function clearHistory(session_id) {
  return request({
    url: '/v1/chat/clear',
    method: 'post',
    params: { session_id }
  })
}
