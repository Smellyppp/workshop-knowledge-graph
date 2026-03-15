/**
 * 数据导入 API 服务
 * 封装所有数据导入相关的接口调用
 */
import request from './index'

/**
 * 上传并导入 Excel 文件（一步完成）
 * @param {File} file - Excel 文件对象
 */
export const uploadAndImport = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/v1/data-import/upload-and-import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 300000 // 导入可能需要较长时间，设置5分钟超时
  })
}

/**
 * 获取上传记录列表
 */
export const getUploadRecords = () => {
  return request.get('/v1/data-import/records')
}

/**
 * 获取上传记录详情
 * @param {string} fileId - 文件ID
 */
export const getUploadRecord = (fileId) => {
  return request.get(`/v1/data-import/records/${fileId}`)
}

/**
 * 删除上传记录
 * @param {string} fileId - 文件ID
 */
export const deleteUploadRecord = (fileId) => {
  return request.delete(`/v1/data-import/records/${fileId}`)
}

/**
 * 根据历史记录重新导入
 * @param {string} fileId - 历史上传记录的文件ID
 */
export const reimportFromRecord = (fileId) => {
  return request.post(`/v1/data-import/reimport/${fileId}`, {}, {
    timeout: 300000 // 导入可能需要较长时间，设置5分钟超时
  })
}

/**
 * 健康检查
 */
export const healthCheck = () => {
  return request.get('/v1/data-import/health')
}

// 统一导出
export const dataImportApi = {
  uploadAndImport,
  getUploadRecords,
  getUploadRecord,
  deleteUploadRecord,
  reimportFromRecord,
  healthCheck
}

export default dataImportApi
