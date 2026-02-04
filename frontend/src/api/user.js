/**
 * 用户相关 API 接口
 * 封装所有用户管理的 HTTP 请求
 */
import request from './index'

export const userApi = {
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数（分页、筛选等）
   * @returns {Promise} 用户列表
   */
  getUsers(params) {
    return request.get('/v1/users', { params })
  },

  /**
   * 根据 ID 获取用户
   * @param {number} id - 用户 ID
   * @returns {Promise} 用户信息
   */
  getUserById(id) {
    return request.get(`/v1/users/${id}`)
  },

  /**
   * 创建新用户
   * @param {Object} data - 用户数据
   * @returns {Promise} 创建的用户
   */
  createUser(data) {
    return request.post('/v1/users', data)
  },

  /**
   * 更新用户信息
   * @param {number} id - 用户 ID
   * @param {Object} data - 更新数据
   * @returns {Promise} 更新后的用户
   */
  updateUser(id, data) {
    return request.put(`/v1/users/${id}`, data)
  },

  /**
   * 删除用户
   * @param {number} id - 用户 ID
   * @returns {Promise}
   */
  deleteUser(id) {
    return request.delete(`/v1/users/${id}`)
  }
}
