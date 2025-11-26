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
              class="input-textarea"
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
              <JsMindViewer
                :data="testCaseData"
                :editable="true"
                @node-click="handleNodeClick"
                @data-change="handleDataChange"
                ref="jsMindRef"
              />
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 导出格式选择对话框 -->
    <el-dialog v-model="showExportDialog" title="选择导出格式" width="500px">
      <div class="format-selection">
        <div class="format-cards">
          <div
            class="format-card"
            :class="{ active: selectedExportFormat === 'json' }"
            @click="selectedExportFormat = 'json'"
          >
            <div class="format-header">
              <el-icon class="format-icon"><Document /></el-icon>
              <h3>JSON 格式</h3>
            </div>
            <div class="format-desc">
              <p>结构化数据格式，便于程序解析和处理</p>
              <ul>
                <li>完整保留所有测试数据</li>
                <li>便于程序读取和编辑</li>
                <li>支持数据处理和备份</li>
              </ul>
            </div>
            <div class="format-features">
              <el-tag type="success" size="small">完整数据</el-tag>
              <el-tag type="info" size="small">程序友好</el-tag>
            </div>
          </div>

          <div
            class="format-card"
            :class="{ active: selectedExportFormat === 'xmind' }"
            @click="selectedExportFormat = 'xmind'"
          >
            <div class="format-header">
              <el-icon class="format-icon"><Share /></el-icon>
              <h3>XMind 格式</h3>
            </div>
            <div class="format-desc">
              <p>专业思维导图格式，兼容XMind软件</p>
              <ul>
                <li>思维导图可视化展示</li>
                <li>支持XMind专业软件</li>
                <li>便于团队协作和展示</li>
              </ul>
            </div>
            <div class="format-features">
              <el-tag type="warning" size="small">可视化</el-tag>
              <el-tag type="primary" size="small">专业软件</el-tag>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExport">
          <el-icon><Download /></el-icon>
          确认导出
        </el-button>
      </template>
    </el-dialog>

      </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import JsMindViewer from '@/components/JsMindViewer.vue'
import type { TestCaseNode, UploadFile } from '@/types'

// 响应式数据
const inputText = ref('')
const uploadedFile = ref<File | null>(null)
const generating = ref(false)
const testCaseData = ref<TestCaseNode | null>(null)
const jsMindRef = ref<InstanceType<typeof JsMindViewer>>()

// 导出相关数据
const showExportDialog = ref(false)
const selectedExportFormat = ref('json')


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
  testCaseData.value = JSON.parse(JSON.stringify(sampleTestCaseData))
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

  // 显示格式选择卡片
  showExportDialog.value = true
}

const confirmExport = () => {
  if (selectedExportFormat.value === 'json') {
    exportAsJSON()
  } else if (selectedExportFormat.value === 'xmind') {
    exportAsXMind()
  }
  showExportDialog.value = false
}

const exportAsJSON = () => {
  const dataStr = JSON.stringify(testCaseData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `test_case_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('JSON格式测试用例导出成功')
}

const exportAsXMind = async () => {
  try {
    // 动态导入JSZip用于创建ZIP文件
    const JSZip = await import('jszip')
    const zip = new JSZip.default()

    // 生成content.xml内容
    const xmindContent = generateSimpleXMind(testCaseData.value!)

    // 添加必要的XMind文件结构
    zip.file('content.xml', xmindContent)

    // 添加META-INF目录和manifest.xml
    const manifestContent = generateManifestXML()
    zip.file('META-INF/manifest.xml', manifestContent)

    // 生成ZIP文件
    const zipBlob = await zip.generateAsync({ type: 'blob' })

    const url = URL.createObjectURL(zipBlob)
    const link = document.createElement('a')
    link.href = url

    // 使用测试用例的一级标题作为文件名
    const fileName = testCaseData.value?.label || '测试用例'
    const safeFileName = fileName.replace(/[\\/:*?"<>|]/g, '_') + '.xmind'
    link.download = safeFileName

    link.click()
    URL.revokeObjectURL(url)

    ElMessage.success('XMind格式测试用例导出成功')
  } catch (error) {
    ElMessage.error('XMind导出失败')
    console.error('XMind export error:', error)
  }
}

const generateSimpleXMind = (node: TestCaseNode): string => {
  const convertNode = (n: TestCaseNode, level: number = 0): string => {
    const indent = '  '.repeat(level)

    // 统一使用简单的topic结构，避免复杂的嵌套
    let result = `${indent}<topic id="${n.id}" timestamp="${Date.now()}">\n`
    result += `${indent}  <title>${escapeXML(n.label)}</title>\n`

    // 简化扩展数据，避免复杂的结构
    if (n.data?.testType || n.data?.steps?.length || n.data?.expected) {
      result += `${indent}  <notes>\n`
      result += `${indent}    <plain>${escapeXML(n.label)}\n\n`

      if (n.data?.testType) {
        result += `测试类型: ${escapeXML(n.data.testType)}\n\n`
      }
      if (n.data?.steps?.length) {
        result += `测试步骤:\n`
        n.data.steps.forEach((step, index) => {
          result += `${index + 1}. ${escapeXML(step)}\n`
        })
        result += `\n`
      }
      if (n.data?.expected) {
        result += `预期结果: ${escapeXML(n.data.expected)}\n`
      }

      result += `</plain>\n`
      result += `${indent}  </notes>\n`
    }

    // 递归处理子节点
    if (n.children && n.children.length > 0) {
      result += `${indent}  <children>\n`
      result += `${indent}    <topics type="attached">\n`
      n.children.forEach(child => {
        result += convertNode(child, level + 2)
      })
      result += `${indent}    </topics>\n`
      result += `${indent}  </children>\n`
    }

    result += `${indent}</topic>\n`
    return result
  }

  // 使用更简单但兼容的XMind结构
  return `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:1.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0">
  <sheet id="sheet_${Date.now()}" theme="theme_${Date.now()}">
    <title>${escapeXML(node.label)}</title>
    ${convertNode(node)}
  </sheet>
</xmap-content>`
}

const generateManifestXML = (): string => {
  return `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0" version="1.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
  <file-entry full-path="META-INF/" media-type=""/>
  <file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
</manifest>`
}

const generateStylesXML = (): string => {
  return `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:1.0" version="1.0">
</xmap-styles>`
}

const escapeXML = (text: string): string => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const handleNodeClick = (node: TestCaseNode) => {
  ElMessage.info(`选择了节点: ${node.label}`)
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
  width: 38%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 400px;
}

.right-section {
  flex: 1;
  min-width: 500px;
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

.input-textarea {
  width: 100%;
}

:deep(.input-textarea .el-textarea__inner) {
  width: 100%;
  min-height: 300px;
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

/* 响应式设计 */
@media (max-width: 1600px) {
  .left-section {
    width: 40%;
    min-width: 380px;
  }

  .right-section {
    min-width: 450px;
  }
}

@media (max-width: 1200px) {
  .design-container {
    flex-direction: column;
    gap: 16px;
    min-height: auto;
  }

  .left-section {
    width: 100%;
    min-width: auto;
    max-height: 400px;
    overflow-y: auto;
  }

  .right-section {
    min-width: auto;
    min-height: 500px;
  }

  .upload-card {
    min-height: 160px;
  }

  :deep(.input-textarea .el-textarea__inner) {
    min-height: 200px;
  }
}

@media (max-width: 768px) {
  .test-case-design {
    height: auto;
    min-height: 100vh;
  }

  .design-container {
    gap: 12px;
  }

  .left-section {
    gap: 12px;
    max-height: none;
  }

  .right-section {
    min-height: 400px;
  }

  .upload-card,
  .input-card,
  .output-card {
    height: auto;
    min-height: auto;
  }

  .input-actions {
    flex-direction: column;
    gap: 8px;
  }

  .output-actions {
    gap: 4px;
  }

  .section-header {
    flex-wrap: wrap;
    gap: 4px;
  }
}

/* 导出格式选择卡片样式 */
.format-selection {
  padding: 8px 0;
}

.format-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.format-card {
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.format-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.format-card.active {
  border-color: #409eff;
  background-color: #ecf5ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.format-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.format-icon {
  font-size: 28px;
  color: #409eff;
}

.format-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.format-desc p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
}

.format-desc ul {
  margin: 0;
  padding-left: 16px;
  color: #909399;
  font-size: 13px;
}

.format-desc li {
  margin-bottom: 2px;
}

.format-features {
  margin-top: 12px;
  display: flex;
  gap: 6px;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .format-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .format-card {
    padding: 12px;
  }

  .format-header h3 {
    font-size: 16px;
  }

  .format-icon {
    font-size: 24px;
  }
}
</style>