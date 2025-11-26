// 文档相关类型
export interface Document {
  id: string
  title: string
  content: string
  tags: string[]
  uploadTime: Date
  filePath?: string
}

// 筛选条件类型
export interface FilterConditions {
  title?: string
  tags: string[]
}

// 分页类型
export interface Pagination {
  current: number
  pageSize: number
  total: number
}

// 测试用例节点类型（用于思维导图）
export interface TestCaseNode {
  id: string
  label: string
  children?: TestCaseNode[]
  data?: any
}

// 上传文件类型
export interface UploadFile {
  name: string
  size: number
  type: string
  content?: string
}