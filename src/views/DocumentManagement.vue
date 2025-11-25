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
          <el-form-item label="模糊搜索：">
            <el-input
              v-model="filterConditions.keyword"
              placeholder="搜索文档内容"
              clearable
              style="width: 200px"
              @input="handleFilter"
            />
          </el-form-item>

          <el-form-item label="文档标题：">
            <el-input
              v-model="filterConditions.title"
              placeholder="搜索文档标题"
              clearable
              style="width: 200px"
              @input="handleFilter"
            />
          </el-form-item>

          <el-form-item label="标签筛选：">
            <el-select
              v-model="filterConditions.tags"
              multiple
              placeholder="选择标签"
              style="width: 200px"
              @change="handleFilter"
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

        <el-table :data="filteredDocuments" stripe style="width: 100%">
          <el-table-column type="index" label="序号" width="80" />

          <el-table-column prop="title" label="文档标题" min-width="200">
            <template #default="{ row }">
              <el-link type="primary" @click="viewDocument(row)">
                {{ row.title }}
              </el-link>
            </template>
          </el-table-column>

          <el-table-column prop="uploadTime" label="上传时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.uploadTime) }}
            </template>
          </el-table-column>

          <el-table-column label="标签栏" min-width="200">
            <template #default="{ row, $index }">
              <el-tag
                v-for="(tag, index) in row.tags"
                :key="index"
                size="small"
                style="margin-right: 4px; margin-bottom: 4px"
                closable
                @close="removeTag($index, index)"
              >
                {{ tag }}
              </el-tag>
              <el-button
                v-if="!showTagInput[$index]"
                size="small"
                style="margin-left: 4px"
                @click="showAddTag($index)"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
              <el-input
                v-if="showTagInput[$index]"
                v-model="newTag"
                size="small"
                style="width: 100px; margin-left: 4px"
                @blur="addTag($index)"
                @keyup.enter="addTag($index)"
              />
            </template>
          </el-table-column>

          <el-table-column label="操作栏" width="240">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="editDocument(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="success" @click="downloadDocument(row)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button size="small" type="danger" @click="deleteDocument(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
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

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑文档" width="800px">
      <el-form :model="editForm">
        <el-form-item label="文档标题：">
          <el-input v-model="editForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="标签：">
          <el-input v-model="editForm.tags" placeholder="请输入标签，用逗号分隔" />
        </el-form-item>
        <el-form-item label="文档内容：">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入文档内容"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmEdit">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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
  keyword: '',
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
const showEditDialog = ref(false)
const uploadFile = ref<File | null>(null)
const showTagInput = ref<Record<number, boolean>>({})
const newTag = ref('')

// 表单数据
const uploadForm = reactive({
  title: '',
  tags: ''
})

const editForm = reactive({
  id: '',
  title: '',
  content: '',
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

const filteredDocuments = computed(() => {
  let filtered = documents.value

  // 模糊搜索（文档内容）
  if (filterConditions.keyword) {
    const keyword = filterConditions.keyword.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.content.toLowerCase().includes(keyword)
    )
  }

  // 标题搜索
  if (filterConditions.title) {
    const title = filterConditions.title.toLowerCase()
    filtered = filtered.filter(doc =>
      doc.title.toLowerCase().includes(title)
    )
  }

  // 标签筛选（且关系）
  if (filterConditions.tags.length > 0) {
    filtered = filtered.filter(doc =>
      filterConditions.tags.every(tag => doc.tags.includes(tag))
    )
  }

  pagination.total = filtered.length

  // 分页
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// 方法
const handleFilter = () => {
  pagination.current = 1
}

const resetFilter = () => {
  filterConditions.keyword = ''
  filterConditions.title = ''
  filterConditions.tags = []
  pagination.current = 1
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.current = 1
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
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
  ElMessage.info(`查看文档: ${doc.title}`)
}

const editDocument = (doc: Document) => {
  editForm.id = doc.id
  editForm.title = doc.title
  editForm.content = doc.content
  editForm.tags = doc.tags.join(', ')
  showEditDialog.value = true
}

const confirmEdit = () => {
  const docIndex = documents.value.findIndex(doc => doc.id === editForm.id)
  if (docIndex !== -1) {
    documents.value[docIndex].title = editForm.title
    documents.value[docIndex].content = editForm.content
    documents.value[docIndex].tags = editForm.tags
      ? editForm.tags.split(',').map(tag => tag.trim()).filter(Boolean)
      : []
    ElMessage.success('文档修改成功')
    showEditDialog.value = false
  }
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
  pagination.total = documents.value.length
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
</style>