<template>
  <div class="document-management">
    <!-- 筛选条件区域 -->
    <div class="filter-section">
      <el-card class="filter-card">
        <template #header>
          <div class="filter-header">
            <el-icon><Search /></el-icon>
            <span>筛选条件</span>
          </div>
        </template>

        <el-form :model="filterConditions" :inline="true" class="filter-form">
          <el-form-item label="文档标题：">
            <el-input
              v-model="filterConditions.title"
              placeholder="搜索文档标题"
              clearable
              class="filter-input"
            />
          </el-form-item>

          <el-form-item label="标签筛选：">
            <el-select
              v-model="filterConditions.tags"
              multiple
              placeholder="选择标签"
              class="filter-select"
              clearable
            >
              <el-option
                v-for="tag in availableTags"
                :key="tag"
                :label="tag"
                :value="tag"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleFilter">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 列表展示区域 -->
    <div class="list-section">
      <el-card class="list-card">
        <template #header>
          <div class="list-header">
            <div class="list-title">
              <el-icon><Document /></el-icon>
              <span>文档列表</span>
            </div>
            <el-button type="primary" @click="showUploadDialog = true">
              <el-icon><Upload /></el-icon>
              上传文档
            </el-button>
          </div>
        </template>

        <el-table :data="filteredDocuments" stripe class="document-table">
          <el-table-column type="index" label="序号" width="80" />

          <el-table-column prop="title" label="文档标题" min-width="300">
            <template #default="{ row }">
              <el-link type="primary" @click="viewDocument(row)" class="document-title">
                {{ row.title }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column prop="uploadTime" label="上传时间" width="200">
            <template #default="{ row }">
              {{ formatDate(row.uploadTime) }}
            </template>
          </el-table-column>

          <el-table-column label="标签栏" min-width="250">
            <template #default="{ row, $index }">
              <div class="tag-container">
                <el-tag
                  v-for="(tag, index) in row.tags"
                  :key="index"
                  size="small"
                  class="tag-item"
                  closable
                  @close="removeTag($index, index)"
                >
                  {{ tag }}
                </el-tag>
                <el-button
                  v-if="!showTagInput[$index]"
                  size="small"
                  class="add-tag-btn"
                  @click="showAddTag($index)"
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
                <el-input
                  v-if="showTagInput[$index]"
                  v-model="newTag"
                  size="small"
                  class="tag-input"
                  ref="tagInputRefs"
                  @blur="addTag($index)"
                  @keyup.enter="addTag($index)"
                  @keyup.esc="cancelAddTag($index)"
                />
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作栏" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="success" @click="downloadDocument(row)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button size="small" type="danger" @click="deleteDocument(row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传文档" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".txt,.md,.doc,.docx,.pdf"
        drag
        @change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .txt/.md/.doc/.docx/.pdf 文件，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>

      <el-form v-if="uploadFile" :model="uploadForm" style="margin-top: 20px">
        <el-form-item label="文档标题：">
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="标签：">
          <el-input v-model="uploadForm.tags" placeholder="请输入标签，用逗号分隔" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmUpload">确认上传</el-button>
      </template>
    </el-dialog>

  
    <!-- 预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="文档预览" width="900px" class="preview-dialog">
      <div v-if="selectedDocument" class="preview-content">
        <!-- 文档头部信息 -->
        <div class="preview-header">
          <div class="document-info">
            <div class="document-meta">
              <span class="meta-item">
                <el-icon><Calendar /></el-icon>
                上传时间：{{ formatDate(selectedDocument.uploadTime) }}
              </span>
              <span class="meta-item">
                <el-icon><CollectionTag /></el-icon>
                标签：
                <el-tag
                  v-for="(tag, index) in selectedDocument.tags"
                  :key="index"
                  size="small"
                  type="info"
                  style="margin-left: 4px"
                >
                  {{ tag }}
                </el-tag>
              </span>
            </div>
          </div>
        </div>

        <!-- 文档内容 -->
        <div class="preview-body">
          <div class="content-label">
            <el-icon><DocumentIcon /></el-icon>
            文档内容
          </div>
          <div class="content-text">
            {{ selectedDocument.content }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Upload, Delete, Calendar, CollectionTag, Document as DocumentIcon
} from '@element-plus/icons-vue'
import type { Document, FilterConditions, Pagination } from '@/types'

// 响应式数据
const documents = ref<Document[]>([
  {
    id: '1',
    title: '用户登录功能需求文档',
    content: '这是一个关于用户登录功能的详细需求说明...',
    tags: ['用户管理', '登录', '需求'],
    uploadTime: new Date('2024-01-15')
  },
  {
    id: '2',
    title: '支付系统接口文档',
    content: '支付系统相关接口的详细说明...',
    tags: ['支付', '接口', 'API'],
    uploadTime: new Date('2024-01-14')
  },
  {
    id: '3',
    title: '数据库设计规范',
    content: '数据库设计的相关规范和最佳实践...',
    tags: ['数据库', '设计', '规范'],
    uploadTime: new Date('2024-01-13')
  }
])

const filterConditions = reactive<FilterConditions>({
  title: '',
  tags: []
})

const pagination = reactive<Pagination>({
  current: 1,
  pageSize: 20,
  total: 0
})

// 对话框控制
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const uploadFile = ref<File | null>(null)
const showTagInput = ref<Record<number, boolean>>({})
const newTag = ref('')
const selectedDocument = ref<Document | null>(null)

// 表单数据
const uploadForm = reactive({
  title: '',
  tags: ''
})

// 计算属性
const availableTags = computed(() => {
  const tagSet = new Set<string>()
  documents.value.forEach(doc => {
    doc.tags.forEach(tag => tagSet.add(tag))
  })
  return Array.from(tagSet)
})

const filteredDocuments = ref<Document[]>([])
const allFilteredDocuments = ref<Document[]>([])

const applyFilter = () => {
  let filtered = documents.value

  // 标题搜索
  if (filterConditions.title) {
    const title = filterConditions.title.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(title)
    )
  }

  // 标签筛选（或关系）
  if (filterConditions.tags.length > 0) {
    filtered = filtered.filter(doc =>
      filterConditions.tags.some(tag => doc.tags.includes(tag))
    )
  }

  allFilteredDocuments.value = filtered
  pagination.total = filtered.length

  // 重置到第一页
  pagination.current = 1

  // 应用分页
  applyPagination()
}

const applyPagination = () => {
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  filteredDocuments.value = allFilteredDocuments.value.slice(start, end)
}

// 方法
const handleFilter = () => {
  applyFilter()
}

const resetFilter = () => {
  filterConditions.title = ''
  filterConditions.tags = []
  applyFilter()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.current = 1
  applyPagination()
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
  applyPagination()
}

const formatDate = (date: Date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const handleFileChange = (file: any) => {
  uploadFile.value = file.raw
  uploadForm.title = file.name.replace(/\.[^/.]+$/, '')
}

const confirmUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  if (!uploadForm.title) {
    ElMessage.warning('请输入文档标题')
    return
  }

  // 模拟文件上传
  const newDoc: Document = {
    id: Date.now().toString(),
    title: uploadForm.title,
    content: `文件 ${uploadFile.value.name} 的内容...`,
    tags: uploadForm.tags ? uploadForm.tags.split(',').map(tag => tag.trim()).filter(Boolean) : [],
    uploadTime: new Date(),
    filePath: uploadFile.value.name
  }

  documents.value.unshift(newDoc)
  ElMessage.success('文档上传成功')

  // 重置表单
  showUploadDialog.value = false
  uploadFile.value = null
  uploadForm.title = ''
  uploadForm.tags = ''
}

const viewDocument = (doc: Document) => {
  selectedDocument.value = doc
  showPreviewDialog.value = true
}


const downloadDocument = (doc: Document) => {
  // 模拟下载
  const content = `${doc.title}\n\n${doc.content}\n\n标签: ${doc.tags.join(', ')}`
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${doc.title}.txt`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('文档下载成功')
}

const deleteDocument = (doc: Document) => {
  ElMessageBox.confirm(
    `确定要删除文档 "${doc.title}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = documents.value.findIndex(d => d.id === doc.id)
    if (index !== -1) {
      documents.value.splice(index, 1)
      ElMessage.success('文档删除成功')
    }
  })
}

const showAddTag = (index: number) => {
  showTagInput.value[index] = true
  newTag.value = ''
  // 自动聚焦到输入框
  nextTick(() => {
    const inputRefs = document.querySelectorAll('.tag-input input')
    if (inputRefs[index]) {
      inputRefs[index].focus()
    }
  })
}

const cancelAddTag = (index: number) => {
  showTagInput.value[index] = false
  newTag.value = ''
}

const addTag = (index: number) => {
  if (newTag.value.trim()) {
    const realIndex = documents.value.findIndex(doc =>
      filteredDocuments.value[index] === doc
    )
    if (realIndex !== -1) {
      documents.value[realIndex].tags.push(newTag.value.trim())
    }
  }
  showTagInput.value[index] = false
  newTag.value = ''
}

const removeTag = (rowIndex: number, tagIndex: number) => {
  const realIndex = documents.value.findIndex(doc =>
    filteredDocuments.value[rowIndex] === doc
  )
  if (realIndex !== -1) {
    documents.value[realIndex].tags.splice(tagIndex, 1)
  }
}

onMounted(() => {
  applyFilter()
})
</script>

<style scoped>
.document-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.filter-input {
  width: 240px;
}

.filter-select {
  width: 240px;
}

.document-table {
  width: 100%;
}

.document-title {
  font-weight: 500;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.tag-item {
  margin-right: 4px;
  margin-bottom: 4px;
}

.add-tag-btn {
  margin-left: 4px;
}

.tag-input {
  width: 120px;
  margin-left: 4px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.list-section {
  flex: 1;
}

.list-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-upload-dragger) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .filter-input,
  .filter-select {
    width: 200px;
  }
}

@media (max-width: 1200px) {
  .document-management {
    gap: 16px;
  }

  .filter-form {
    gap: 12px;
  }

  .filter-input,
  .filter-select {
    width: 180px;
  }

  .document-table :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
}

@media (max-width: 768px) {
  .document-management {
    gap: 12px;
  }

  .filter-form {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .filter-form .el-form-item {
    margin-bottom: 0;
  }

  .filter-input,
  .filter-select {
    width: 100%;
  }

  .filter-form .el-form-item:last-child {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 8px;
  }

  .tag-input {
    width: 100px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}

/* 预览对话框样式 */
:deep(.preview-dialog) {
  border-radius: 12px;
}

.preview-content {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-header {
  padding: 20px 0;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

.document-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.document-title {
  margin: 0;
  font-size: 14px;
  font-weight: normal;
  color: #409eff;
  line-height: 1.4;
}

.document-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.meta-item .el-icon {
  font-size: 16px;
  color: #909399;
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding: 8px 0;
  border-bottom: 2px solid #e4e7ed;
}

.content-label .el-icon {
  font-size: 18px;
  color: #409eff;
}

.content-text {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  line-height: 1.8;
  font-size: 14px;
  color: #495057;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

:deep(.preview-dialog .el-dialog__body) {
  padding: 24px;
}

/* 预览对话框响应式 */
@media (max-width: 768px) {
  :deep(.preview-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }

  .document-meta {
    flex-direction: column;
    gap: 6px;
  }

  .content-text {
    padding: 16px;
    font-size: 13px;
  }
}
</style>