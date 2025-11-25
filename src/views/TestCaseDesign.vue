<template>
  <div class="test-case-design">
    <div class="design-container">
      <!-- 左侧区域 -->
      <div class="left-section">
        <!-- 文件上传区域 -->
        <div class="upload-section">
          <el-card class="upload-card">
            <template #header>
              <div class="section-header">
                <el-icon><Upload /></el-icon>
                <span>文件上传</span>
              </div>
            </template>

            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".txt,.md,.doc,.docx,.pdf,.jpg,.jpeg,.png"
              drag
              @change="handleFileChange"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 .txt/.md/.doc/.docx/.pdf/.jpg/.jpeg/.png 文件
                </div>
              </template>
            </el-upload>

            <div v-if="uploadedFile" class="uploaded-file-info">
              <el-alert
                :title="`已上传文件: ${uploadedFile.name}`"
                type="success"
                :closable="false"
                show-icon
              />
            </div>
          </el-card>
        </div>

        <!-- 在线输入区域 -->
        <div class="input-section">
          <el-card class="input-card">
            <template #header>
              <div class="section-header">
                <el-icon><EditPen /></el-icon>
                <span>在线输入</span>
                <el-tag type="info" size="small">{{ inputText.length }}/2028</el-tag>
              </div>
            </template>

            <el-input
              v-model="inputText"
              type="textarea"
              :rows="12"
              placeholder="请输入需求描述文本，支持多语言、数字、特殊字符、空格、回车..."
              maxlength="2028"
              show-word-limit
              @input="handleInputChange"
            />

            <div class="input-actions">
              <el-button @click="clearInput">清空</el-button>
              <el-button type="primary" @click="generateTestCase" :loading="generating">
                <el-icon><Magic /></el-icon>
                生成测试用例
              </el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 右侧用例输出区域 -->
      <div class="right-section">
        <el-card class="output-card">
          <template #header>
            <div class="section-header">
              <el-icon><Share /></el-icon>
              <span>测试用例输出</span>
              <div class="output-actions">
                <el-button size="small" @click="clearOutput" :disabled="!testCaseData">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
                <el-button size="small" @click="exportTestCase" :disabled="!testCaseData">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </div>
          </template>

          <div class="output-content">
            <div v-if="!testCaseData" class="empty-output">
              <el-empty description="暂无测试用例数据">
                <template #image>
                  <el-icon size="100" color="#c0c4cc"><DocumentCopy /></el-icon>
                </template>
                <el-button type="primary" @click="loadSampleData">加载示例数据</el-button>
              </el-empty>
            </div>

            <div v-else class="mind-map-container">
              <MindMap
                :data="testCaseData"
                :editable="true"
                @node-click="handleNodeClick"
                @node-edit="handleNodeEdit"
                @data-change="handleDataChange"
              />
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import MindMap from '@/components/MindMap.vue'
import type { TestCaseNode, UploadFile } from '@/types'

// 响应式数据
const inputText = ref('')
const uploadedFile = ref<File | null>(null)
const generating = ref(false)
const testCaseData = ref<TestCaseNode | null>(null)

// 示例数据
const sampleTestCaseData: TestCaseNode = {
  id: 'root',
  label: '用户登录功能测试',
  children: [
    {
      id: '1',
      label: '正常登录测试',
      children: [
        {
          id: '1-1',
          label: '有效用户名和密码',
          data: {
            testType: 'positive',
            steps: ['打开登录页面', '输入有效用户名', '输入正确密码', '点击登录按钮'],
            expected: '成功登录并跳转到首页'
          }
        },
        {
          id: '1-2',
          label: '邮箱登录',
          data: {
            testType: 'positive',
            steps: ['打开登录页面', '输入邮箱地址', '输入正确密码', '点击登录按钮'],
            expected: '成功登录并跳转到首页'
          }
        }
      ]
    },
    {
      id: '2',
      label: '异常登录测试',
      children: [
        {
          id: '2-1',
          label: '错误密码',
          data: {
            testType: 'negative',
            steps: ['打开登录页面', '输入有效用户名', '输入错误密码', '点击登录按钮'],
            expected: '显示密码错误提示'
          }
        },
        {
          id: '2-2',
          label: '不存在的用户名',
          data: {
            testType: 'negative',
            steps: ['打开登录页面', '输入不存在的用户名', '输入任意密码', '点击登录按钮'],
            expected: '显示用户不存在提示'
          }
        },
        {
          id: '2-3',
          label: '空用户名和密码',
          data: {
            testType: 'negative',
            steps: ['打开登录页面', '不输入用户名', '不输入密码', '点击登录按钮'],
            expected: '显示必填字段提示'
          }
        }
      ]
    },
    {
      id: '3',
      label: '界面测试',
      children: [
        {
          id: '3-1',
          label: '页面元素显示',
          data: {
            testType: 'ui',
            steps: ['打开登录页面'],
            expected: '所有输入框、按钮、链接正确显示'
          }
        },
        {
          id: '3-2',
          label: '响应式设计',
          data: {
            testType: 'ui',
            steps: ['在不同设备尺寸下打开登录页面'],
            expected: '页面布局正确适配'
          }
        }
      ]
    }
  ]
}

// 方法
const handleFileChange = (file: any) => {
  uploadedFile.value = file.raw

  // 模拟文件内容读取
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target?.result as string
    if (inputText.value.length + content.length <= 2028) {
      inputText.value += content
    } else {
      ElMessage.warning('文件内容加上已有输入超过字符限制')
    }
  }

  if (uploadedFile.value.type.startsWith('image/')) {
    // 对于图片，模拟OCR识别结果
    setTimeout(() => {
      inputText.value += '\n[图片OCR识别结果]: 这是一个包含用户登录流程的界面截图，包含用户名输入框、密码输入框和登录按钮。'
    }, 1000)
  } else {
    reader.readAsText(uploadedFile.value)
  }
}

const handleInputChange = () => {
  // 输入变化时的处理逻辑
  if (inputText.value.length > 2028) {
    ElMessage.error('输入内容不能超过2028个字符')
    inputText.value = inputText.value.substring(0, 2028)
  }
}

const clearInput = () => {
  inputText.value = ''
  uploadedFile.value = null
}

const generateTestCase = async () => {
  if (!inputText.value.trim() && !uploadedFile.value) {
    ElMessage.warning('请输入需求描述或上传文件')
    return
  }

  generating.value = true

  try {
    // 模拟AI生成过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 这里应该调用后端AI接口，现在使用示例数据
    testCaseData.value = { ...sampleTestCaseData }

    ElMessage.success('测试用例生成成功！')
  } catch (error) {
    ElMessage.error('生成测试用例失败，请重试')
  } finally {
    generating.value = false
  }
}

const loadSampleData = () => {
  testCaseData.value = { ...sampleTestCaseData }
  ElMessage.success('示例数据加载成功')
}

const clearOutput = () => {
  testCaseData.value = null
}

const exportTestCase = () => {
  if (!testCaseData.value) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  // 导出为JSON格式
  const dataStr = JSON.stringify(testCaseData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `test_case_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('测试用例导出成功')
}

const handleNodeClick = (node: TestCaseNode) => {
  console.log('Node clicked:', node)
  ElMessage.info(`点击了节点: ${node.label}`)
}

const handleNodeEdit = (node: TestCaseNode) => {
  console.log('Node edited:', node)
}

const handleDataChange = (data: TestCaseNode) => {
  testCaseData.value = data
}
</script>

<style scoped>
.test-case-design {
  height: 100%;
}

.design-container {
  display: flex;
  gap: 20px;
  height: 100%;
  min-height: 700px;
}

.left-section {
  width: 40%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-section {
  flex: 1;
}

.upload-card,
.input-card,
.output-card {
  height: 100%;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
}

.upload-section {
  flex: 0 0 auto;
}

.upload-card {
  min-height: 200px;
}

.uploaded-file-info {
  margin-top: 16px;
}

.input-section {
  flex: 1;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.output-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.output-content {
  height: calc(100% - 60px);
}

.empty-output {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mind-map-container {
  height: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-upload-dragger) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  width: 100%;
  min-height: 120px;
}

:deep(.el-card__body) {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

:deep(.el-textarea__inner) {
  resize: none;
}
</style>