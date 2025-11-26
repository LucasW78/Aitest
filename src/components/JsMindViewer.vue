<template>
  <div class="jsmind-viewer">
    <div class="jsmind-toolbar">
      <el-button-group size="small">
        <el-tooltip content="放大" placement="top">
          <el-button @click="zoomIn" :disabled="zoomLevel >= 2">
            <el-icon><ZoomIn /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="缩小" placement="top">
          <el-button @click="zoomOut" :disabled="zoomLevel <= 0.3">
            <el-icon><ZoomOut /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="重置大小" placement="top">
          <el-button @click="resetZoom">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-button-group size="small" style="margin-left: 8px">
        <el-button @click="expandAll">
          <el-icon><Plus /></el-icon>
          展开
        </el-button>
        <el-button @click="collapseAll">
          <el-icon><Minus /></el-icon>
          收起
        </el-button>
      </el-button-group>

      <!-- 键盘快捷键提示 -->
      <el-tooltip effect="dark" placement="top" v-if="editable">
        <template #content>
          <div style="font-size: 12px; line-height: 1.5;">
            <div><strong>键盘快捷键：</strong></div>
            <div>Tab - 添加子节点</div>
            <div>Enter - 添加同级节点</div>
            <div>Delete/Backspace - 删除节点</div>
            <div>双击 - 编辑节点</div>
          </div>
        </template>
        <el-button size="small" style="margin-left: 8px;">
          <el-icon><QuestionFilled /></el-icon>
        </el-button>
      </el-tooltip>
    </div>

    <div id="jsmind_container" class="jsmind-container"></div>

    <!-- 节点编辑对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title=""
      width="600px"
      :show-close="false"
      class="node-edit-dialog"
      align-center
    >
      <!-- 自定义标题 -->
      <div class="dialog-header">
        <div class="header-content">
          <div class="header-icon">
            <el-icon size="24" color="#409eff"><Edit /></el-icon>
          </div>
          <div class="header-text">
            <h3 class="dialog-title">编辑测试节点</h3>
            <p class="dialog-subtitle">完善节点信息，让测试用例更加清晰</p>
          </div>
        </div>
        <el-button
          class="close-btn"
          @click="showEditDialog = false"
          :icon="Close"
          circle
          size="small"
        />
      </div>

      <div class="dialog-content">
        <el-form :model="editForm" class="edit-form">
          <!-- 节点名称 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-icon">
                <el-icon size="16" color="#606266"><Document /></el-icon>
              </div>
              <span class="section-title">节点名称</span>
            </div>
            <el-form-item class="form-item">
              <el-input
                v-model="editForm.topic"
                placeholder="请输入节点名称，如：登录功能验证"
                class="custom-input"
                size="large"
              />
            </el-form-item>
          </div>

          <!-- 测试类型 -->
          <div class="form-section" v-if="isTestCaseNode">
            <div class="section-header">
              <div class="section-icon">
                <el-icon size="16" color="#606266"><Flag /></el-icon>
              </div>
              <span class="section-title">测试类型</span>
            </div>
            <el-form-item class="form-item">
              <el-select
                v-model="editForm.testType"
                placeholder="请选择测试类型"
                class="custom-select"
                size="large"
              >
                <el-option label="正向测试" value="positive">
                  <div class="option-item">
                    <el-icon color="#67c23a"><CircleCheck /></el-icon>
                    <span>正向测试</span>
                  </div>
                </el-option>
                <el-option label="负向测试" value="negative">
                  <div class="option-item">
                    <el-icon color="#f56c6c"><CircleClose /></el-icon>
                    <span>负向测试</span>
                  </div>
                </el-option>
                <el-option label="边界测试" value="boundary">
                  <div class="option-item">
                    <el-icon color="#e6a23c"><Warning /></el-icon>
                    <span>边界测试</span>
                  </div>
                </el-option>
                <el-option label="UI测试" value="ui">
                  <div class="option-item">
                    <el-icon color="#909399"><Monitor /></el-icon>
                    <span>UI测试</span>
                  </div>
                </el-option>
                <el-option label="性能测试" value="performance">
                  <div class="option-item">
                    <el-icon color="#409eff"><Timer /></el-icon>
                    <span>性能测试</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </div>

          <!-- 测试步骤 -->
          <div class="form-section" v-if="isTestCaseNode">
            <div class="section-header">
              <div class="section-icon">
                <el-icon size="16" color="#606266"><List /></el-icon>
              </div>
              <span class="section-title">测试步骤</span>
            </div>
            <el-form-item class="form-item">
              <el-input
                v-model="editForm.steps"
                type="textarea"
                :rows="4"
                placeholder="请输入测试步骤，每行一个步骤&#10;例如：&#10;1. 打开登录页面&#10;2. 输入用户名和密码&#10;3. 点击登录按钮"
                class="custom-textarea"
                resize="none"
              />
            </el-form-item>
          </div>

          <!-- 预期结果 -->
          <div class="form-section" v-if="isTestCaseNode">
            <div class="section-header">
              <div class="section-icon">
                <el-icon size="16" color="#606266"><Select /></el-icon>
              </div>
              <span class="section-title">预期结果</span>
            </div>
            <el-form-item class="form-item">
              <el-input
                v-model="editForm.expected"
                type="textarea"
                :rows="3"
                placeholder="请输入预期结果&#10;例如：成功登录并跳转到系统首页"
                class="custom-textarea"
                resize="none"
              />
            </el-form-item>
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button
            @click="showEditDialog = false"
            size="large"
            class="cancel-btn"
          >
            取消
          </el-button>
          <el-button
            type="primary"
            @click="confirmEdit"
            size="large"
            class="confirm-btn"
          >
            <el-icon><Check /></el-icon>
            确认保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick, onUnmounted as onUnmountedVue } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ZoomIn,
  ZoomOut,
  RefreshRight,
  Plus,
  Minus,
  Delete,
  Edit,
  QuestionFilled,
  Tools,
  UploadFilled,
  Document,
  Share,
  Download,
  Magic,
  EditPen,
  Close,
  CircleCheck,
  CircleClose,
  Warning,
  Monitor,
  Timer,
  List,
  Select,
  Flag,
  Check
} from '@element-plus/icons-vue'
import type { TestCaseNode } from '@/types'

// jsmind 通过CDN加载，这里不需要import

interface Props {
  data: TestCaseNode
  editable?: boolean
}

interface Emits {
  (e: 'node-click', node: TestCaseNode): void
  (e: 'data-change', data: TestCaseNode): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const jm = ref<any>(null)
const zoomLevel = ref(1)
const selectedNode = ref<any>(null)
const showEditDialog = ref(false)
const editForm = reactive({
  topic: '',
  testType: '',
  steps: '',
  expected: ''
})

// 计算属性
const isTestCaseNode = computed(() => {
  return selectedNode.value && selectedNode.value.parent !== null
})

// 数据转换函数
const convertTestCaseToJsMind = (testCaseData: TestCaseNode | null) => {
  if (!testCaseData) {
    return {
      meta: {
        name: '空画布',
        author: 'AItestdemo',
        version: '1.0'
      },
      format: 'node_tree',
      data: { id: 'root', topic: '暂无数据', isroot: true }
    }
  }

  const convertNode = (node: TestCaseNode): any => {
    const jsmindNode: any = {
      id: node.id,
      topic: node.label,
      isroot: node.id === 'root'
    }

    if (node.data) {
      jsmindNode.testType = node.data.testType
      jsmindNode.steps = node.data.steps || []
      jsmindNode.expected = node.data.expected || ''
    }

    if (node.children && node.children.length > 0) {
      jsmindNode.children = node.children.map(convertNode)
    }

    return jsmindNode
  }

  return {
    meta: {
      name: '测试用例',
      author: 'AItestdemo',
      version: '1.0'
    },
    format: 'node_tree',
    data: convertNode(testCaseData)
  }
}

const convertJsMindToTestCase = (jsmindData: any): TestCaseNode => {
  const convertNode = (node: any): TestCaseNode => {
    const testCaseNode: TestCaseNode = {
      id: node.id,
      label: node.topic,
      children: node.children ? node.children.map(convertNode) : undefined
    }

    if (node.testType || node.steps || node.expected) {
      testCaseNode.data = {
        testType: node.testType || '',
        steps: node.steps || [],
        expected: node.expected || ''
      }
    }

    return testCaseNode
  }

  return convertNode(jsmindData.data)
}

// 获取当前选中节点的辅助函数
const getCurrentSelectedNode = () => {
  if (!jm.value) return null

  try {
    // 方法1: 尝试获取当前选中的节点
    let currentNode = jm.value.get_selected_node()
    if (currentNode) {
      console.log('方法1 - 找到当前选中节点:', currentNode.id, currentNode.topic)
      selectedNode.value = currentNode
      return currentNode
    }

    // 方法2: 检查DOM元素中是否有选中的节点
    const selectedElement = document.querySelector('.jsmind-selected')
    if (selectedElement) {
      const nodeId = selectedElement.getAttribute('data-node-id')
      if (nodeId) {
        currentNode = jm.value.get_node(nodeId)
        if (currentNode) {
          console.log('方法2 - 通过DOM找到选中节点:', currentNode.id, currentNode.topic)
          selectedNode.value = currentNode
          return currentNode
        }
      }
    }

    // 方法3: 尝试获取所有可见节点，选择第一个
    const allNodes = jm.value.get_data()
    if (allNodes && allNodes.data) {
      const findFirstNode = (node) => {
        if (node.id && node.topic) {
          const foundNode = jm.value.get_node(node.id)
          if (foundNode) {
            console.log('方法3 - 找到第一个可用节点:', foundNode.id, foundNode.topic)
            selectedNode.value = foundNode
            jm.value.select_node(foundNode.id) // 主动选择这个节点
            return foundNode
          }
        }
        if (node.children && node.children.length > 0) {
          for (const child of node.children) {
            const found = findFirstNode(child)
            if (found) return found
          }
        }
        return null
      }

      const foundNode = findFirstNode(allNodes.data)
      if (foundNode) return foundNode
    }

    // 方法4: 最后尝试获取根节点
    const rootNode = jm.value.get_root()
    if (rootNode) {
      console.log('方法4 - 使用根节点作为选中节点:', rootNode.id, rootNode.topic)
      selectedNode.value = rootNode
      jm.value.select_node(rootNode.id) // 主动选择根节点
      return rootNode
    }

    console.log('所有方法都失败，没有找到任何可用节点')
    return null
  } catch (error) {
    console.error('获取选中节点失败:', error)
    return null
  }
}

// 键盘事件处理
const setupKeyboardEvents = () => {
  if (typeof window === 'undefined') return

  const handleKeyDown = (event: KeyboardEvent) => {
    // 动态获取当前选中的节点
    const currentSelected = getCurrentSelectedNode()

    console.log('键盘事件:', event.key, '选中节点:', !!currentSelected)

    if (!jm.value || !currentSelected) {
      console.log('没有选中节点，跳过键盘事件')
      return
    }

    // 防止在输入框中触发
    const target = event.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      console.log('在输入框中，跳过键盘事件')
      return
    }

    console.log('处理键盘快捷键:', event.key)
    event.preventDefault()

    switch (event.key) {
      case 'Tab':
        console.log('执行: 添加子节点')
        addChildNode()
        break
      case 'Enter':
        console.log('执行: 添加同级节点')
        addSiblingNode()
        break
      case 'Delete':
      case 'Backspace':
        console.log('执行: 删除节点')
        removeSelectedNode()
        break
      default:
        console.log('未处理的键:', event.key)
    }
  }

  // 双击编辑节点
  const handleDoubleClick = (event: Event) => {
    if (!jm.value) return

    const target = event.target as HTMLElement
    console.log('双击事件触发，目标元素:', target.className, target.tagName)

    // 尝试多种选择器查找节点元素
    let nodeElement = target.closest('.jsmind-node')
    if (!nodeElement) {
      nodeElement = target.closest('[nodeid]')
    }
    if (!nodeElement) {
      nodeElement = target.closest('.jmnode')
    }

    if (nodeElement) {
      console.log('检测到节点双击:', nodeElement)
      event.preventDefault()
      event.stopPropagation()

      // 尝试获取节点ID
      let nodeId = nodeElement.getAttribute('nodeid') ||
                  nodeElement.getAttribute('data-node-id') ||
                  nodeElement.getAttribute('id')

      console.log('获取到的节点ID:', nodeId)

      if (nodeId) {
        // 选中节点并编辑
        const node = jm.value.get_node(nodeId)
        if (node) {
          console.log('通过双击找到节点，进入编辑:', node.id, node.topic)
          selectedNode.value = node
          jm.value.select_node(nodeId)
          selectAndEditNode(node)
        } else {
          console.log('无法通过ID找到节点，使用当前选中节点')
          editSelectedNode()
        }
      } else {
        console.log('无法获取节点ID，使用当前选中节点')
        editSelectedNode()
      }
    } else {
      console.log('双击的不是节点元素')
    }
  }

  // 添加鼠标点击事件监听
  const handleMouseClick = (event: Event) => {
    // 检查是否点击了节点元素
    const target = event.target as HTMLElement
    const nodeElement = target.closest('.jsmind-node')

    if (nodeElement) {
      console.log('检测到点击节点元素:', nodeElement)

      // 尝试多种方式获取节点ID
      let nodeId = nodeElement.getAttribute('data-node-id') ||
                  nodeElement.getAttribute('nodeid') ||
                  nodeElement.id

      console.log('提取到的节点ID:', nodeId)

      if (nodeId && jm.value) {
        // 尝试通过ID获取节点
        const clickedNode = jm.value.get_node(nodeId)
        if (clickedNode) {
          console.log('通过点击找到节点:', clickedNode.id, clickedNode.topic)
          selectedNode.value = clickedNode
          jm.value.select_node(nodeId) // 确保节点被选中
          return
        }
      }
    }

    // 如果没有找到具体节点，使用通用方法
    setTimeout(() => {
      getCurrentSelectedNode()
    }, 100)
  }

  document.addEventListener('keydown', handleKeyDown)
  document.addEventListener('dblclick', handleDoubleClick)
  document.addEventListener('click', handleMouseClick)

  console.log('键盘事件监听器已设置')

  // 在组件卸载时清理事件监听
  onUnmountedVue(() => {
    document.removeEventListener('keydown', handleKeyDown)
    document.removeEventListener('dblclick', handleDoubleClick)
    document.removeEventListener('click', handleMouseClick)
    console.log('键盘事件监听器已清理')
  })
}

// 添加并编辑子节点
const addChildNode = () => {
  if (!jm.value) return

  try {
    // 动态获取当前选中节点
    const currentSelected = getCurrentSelectedNode()
    if (!currentSelected) {
      ElMessage.warning('请先选择一个节点')
      return
    }

    const nodeId = 'node_' + Date.now()
    const defaultTopic = '新子节点'

    console.log('添加子节点到:', currentSelected.id, currentSelected.topic)

    // 使用jsMind的正确API
    jm.value.add_node(currentSelected.id, nodeId, defaultTopic, {
      testType: 'positive',
      steps: [],
      expected: ''
    })

    // 等待节点添加完成后，自动进入编辑模式
    setTimeout(() => {
      const newNode = jm.value.get_node(nodeId)
      if (newNode) {
        console.log('新节点创建成功，进入编辑模式:', newNode.id, newNode.topic)
        selectAndEditNode(newNode)
      } else {
        ElMessage.success('子节点添加成功')
      }
    }, 100)

  } catch (error) {
    console.error('添加子节点失败:', error)
    ElMessage.error('添加子节点失败')
  }
}

// 添加同级节点
const addSiblingNode = () => {
  if (!jm.value) return

  try {
    // 动态获取当前选中节点
    const currentSelected = getCurrentSelectedNode()
    if (!currentSelected) {
      ElMessage.warning('请先选择一个节点')
      return
    }

    const nodeId = 'node_' + Date.now()

    console.log('当前选中节点详情:', currentSelected)

    // 检查节点属性，寻找父节点信息
    let parentId = null

    // 方法1: 检查parentid属性
    if (currentSelected.parentid !== null && currentSelected.parentid !== undefined) {
      parentId = currentSelected.parentid
      console.log('方法1 - 通过parentid找到父节点:', parentId)
    }
    // 方法2: 检查parent属性
    else if (currentSelected.parent && currentSelected.parent.id) {
      parentId = currentSelected.parent.id
      console.log('方法2 - 通过parent属性找到父节点:', parentId)
    }
    // 方法3: 通过jsMind API获取父节点
    else {
      try {
        const nodeData = jm.value.get_node(currentSelected.id)
        if (nodeData && nodeData.parentid !== null && nodeData.parentid !== undefined) {
          parentId = nodeData.parentid
          console.log('方法3 - 通过API找到父节点:', parentId)
        }
      } catch (apiError) {
        console.log('API方法获取父节点失败:', apiError)
      }
    }

    // 如果还是没有找到父节点，说明可能是根节点
    if (!parentId) {
      // 检查是否真的是根节点
      if (currentSelected.isroot) {
        ElMessage.warning('根节点无法添加同级节点')
        return
      } else {
        // 尝试从数据结构中推断父节点
        const allData = jm.value.get_data()
        parentId = findParentNode(allData.data, currentSelected.id)
        if (parentId) {
          console.log('方法4 - 通过数据结构找到父节点:', parentId)
        } else {
          ElMessage.warning('无法找到父节点，无法添加同级节点')
          return
        }
      }
    }

    // 验证父节点存在
    const parentNode = jm.value.get_node(parentId)
    if (!parentNode) {
      ElMessage.error('父节点不存在')
      return
    }

    console.log('准备添加同级节点:')
    console.log('- 父节点:', parentId, parentNode.topic)
    console.log('- 当前节点:', currentSelected.id, currentSelected.topic)
    console.log('- 新节点ID:', nodeId)

    // 在父节点下添加新节点作为同级节点
    jm.value.add_node(parentId, nodeId, '新同级节点', {
      testType: 'positive',
      steps: [],
      expected: ''
    })

    // 等待节点添加完成后，自动进入编辑模式
    setTimeout(() => {
      const newNode = jm.value.get_node(nodeId)
      if (newNode) {
        console.log('新同级节点创建成功，进入编辑模式:', newNode.id, newNode.topic)
        selectAndEditNode(newNode)
      } else {
        ElMessage.success('同级节点添加成功')
      }
    }, 100)
  } catch (error) {
    console.error('添加同级节点失败:', error)
    ElMessage.error('添加同级节点失败')
  }
}

// 辅助函数：从数据结构中查找父节点
const findParentNode = (node, childId, parentFound = null) => {
  if (node.children && node.children.length > 0) {
    for (const child of node.children) {
      if (child.id === childId) {
        return node.id
      }
      const found = findParentNode(child, childId, node.id)
      if (found) return found
    }
  }
  return parentFound
}

// 选择并编辑节点
const selectAndEditNode = (node: any) => {
  if (!node) return

  try {
    // 选中这个新创建的节点
    jm.value.select_node(node.id)
    selectedNode.value = node

    console.log('选中节点，准备编辑:', node.id, node.topic)

    // 填充编辑表单
    editForm.topic = node.topic || ''
    editForm.testType = node.testType || 'positive'
    editForm.steps = node.steps ? node.steps.join('\n') : ''
    editForm.expected = node.expected || ''

    // 显示编辑对话框
    showEditDialog.value = true

    ElMessage.success(`节点已添加，正在编辑: ${node.topic}`)

  } catch (error) {
    console.error('选择并编辑节点失败:', error)
    ElMessage.error('编辑节点失败')
  }
}

// 测试节点选择
const testSelection = () => {
  console.log('=== 测试节点选择 ===')
  console.log('jm.value:', !!jm.value)
  console.log('selectedNode.value:', selectedNode.value)

  if (!jm.value) {
    console.log('jsMind实例未初始化')
    return
  }

  try {
    // 使用辅助函数获取当前选中节点
    const currentSelected = getCurrentSelectedNode()
    console.log('获取到的选中节点:', currentSelected)

    if (currentSelected) {
      // 验证API可用性
      console.log('测试API可用性:')
      console.log('- jm.value.get_selected_node():', typeof jm.value.get_selected_node)
      console.log('- jm.value.get_root():', typeof jm.value.get_root)
      console.log('- jm.value.select_node():', typeof jm.value.select_node)
      console.log('- jm.value.add_node():', typeof jm.value.add_node)
      console.log('- jm.value.remove_node():', typeof jm.value.remove_node)
      console.log('- jm.value.get_node():', typeof jm.value.get_node)

      ElMessage.success(`已选择节点: ${currentSelected.topic}`)
    } else {
      ElMessage.warning('无法获取选中节点')
    }

  } catch (error) {
    console.error('测试选择失败:', error)
    ElMessage.error('测试选择失败')
  }
}

// 初始化 jsmind
const initJsMind = async () => {
  await nextTick()

  console.log('initJsMind 被调用，当前数据:', props.data)

  if (typeof window !== 'undefined' && window.jsMind) {
    // 清空容器
    const container = document.getElementById('jsmind_container')
    if (container) {
      container.innerHTML = ''
      console.log('jsMind容器已清空')
    }

    const options = {
      container: 'jsmind_container',
      theme: 'primary',
      mode: 'full',
      support_html: true,
      editable: true,
      view: {
        hmargin: 100,
        vmargin: 50,
        line_width: 2,
        line_color: '#ddd'
      },
      layout: {
        hspace: 30,
        vspace: 20,
        pspace: 13
      },
      shortcut: {
        enable: false
      }
    }

    jm.value = new window.jsMind(options)
    console.log('新的jsMind实例已创建')

    const mindData = convertTestCaseToJsMind(props.data)
    console.log('转换后的jsMind数据:', mindData)

    jm.value.show(mindData)
    console.log('jsMind数据已显示')

    // 启用编辑模式
    if (props.editable) {
      jm.value.enable_edit()
      console.log('编辑模式已启用')
    }

    // 绑定事件
    jm.value.add_event_listener((type: string, data: any) => {
      console.log('jsMind事件:', type, data)

      // 尝试不同的事件类型名称
      if (type === 'select_node') {
        console.log('节点被选中 (select_node):', data.node)
        selectedNode.value = data.node
        const testCaseNode = convertJsMindToTestCase({ data: data.node })
        emit('node-click', testCaseNode)
      } else if (type === 'node_selected') {
        console.log('节点被选中 (node_selected):', data.node)
        selectedNode.value = data.node
        const testCaseNode = convertJsMindToTestCase({ data: data.node })
        emit('node-click', testCaseNode)
      } else if (type === 'selected_node') {
        console.log('节点被选中 (selected_node):', data.node)
        selectedNode.value = data.node
        const testCaseNode = convertJsMindToTestCase({ data: data.node })
        emit('node-click', testCaseNode)
      }
    })

    // 添加键盘事件监听
    setupKeyboardEvents()

    // 默认展开所有节点并选择根节点
    setTimeout(() => {
      expandAll()
      console.log('所有节点已展开')

      // 默认选择根节点
      const rootNode = jm.value.get_root()
      if (rootNode) {
        console.log('初始化完成，选择根节点:', rootNode.id, rootNode.topic)
        selectedNode.value = rootNode
        jm.value.select_node(rootNode.id)
      } else {
        console.log('警告：无法获取根节点')
      }

      // 检查容器内容
      const containerAfter = document.getElementById('jsmind_container')
      if (containerAfter) {
        console.log('容器子元素数量:', containerAfter.children.length)
        console.log('容器HTML片段:', containerAfter.innerHTML.substring(0, 200))
      }
    }, 100)
  } else {
    console.log('jsMind库未加载')
  }
}

// 方法
const zoomIn = () => {
  if (jm.value) {
    zoomLevel.value = Math.min(zoomLevel.value + 0.1, 2)
    jm.value.view.zoomIn()
  }
}

const zoomOut = () => {
  if (jm.value) {
    zoomLevel.value = Math.max(zoomLevel.value - 0.1, 0.3)
    jm.value.view.zoomOut()
  }
}

const resetZoom = () => {
  if (jm.value) {
    zoomLevel.value = 1
    // 使用正确的jsMind重置缩放API
    try {
      jm.value.view.setZoom(1)
    } catch (error) {
      // 如果setZoom不可用，尝试其他方法
      console.log('尝试其他重置缩放方法')
      // 重新初始化视图来重置缩放
      const currentData = jm.value.get_data()
      jm.value.show(currentData)
    }
  }
}

const expandAll = () => {
  if (jm.value) {
    jm.value.expand_all()
  }
}

const collapseAll = () => {
  if (jm.value) {
    jm.value.collapse_all()
  }
}

const addSelectedNode = () => {
  console.log('addSelectedNode 被调用')

  // 直接调用addChildNode函数，它已经包含了自动编辑功能
  addChildNode()
}

const removeSelectedNode = () => {
  console.log('removeSelectedNode 被调用')
  if (!jm.value || !selectedNode.value) {
    console.log('没有选中节点，无法删除')
    ElMessage.warning('请先选择要删除的节点')
    return
  }

  console.log('准备删除节点:', selectedNode.value.id, selectedNode.value.topic)

  if (selectedNode.value.isroot) {
    ElMessage.error('不能删除根节点')
    return
  }

  try {
    jm.value.remove_node(selectedNode.value.id)
    selectedNode.value = null
    ElMessage.success('节点删除成功')
  } catch (error) {
    console.error('删除节点失败:', error)
    ElMessage.error('删除节点失败')
  }
}

// 快速编辑选中节点（工具栏按钮用）
const quickEditSelectedNode = () => {
  console.log('quickEditSelectedNode 被调用')

  // 动态获取当前选中节点
  const currentSelected = getCurrentSelectedNode()
  if (!currentSelected) {
    ElMessage.warning('请先选择要编辑的节点')
    return
  }

  console.log('准备编辑节点:', currentSelected.id, currentSelected.topic)
  selectAndEditNode(currentSelected)
}

const editSelectedNode = () => {
  console.log('editSelectedNode 被调用')
  if (!selectedNode.value) {
    console.log('没有选中节点，无法编辑')
    ElMessage.warning('请先选择要编辑的节点')
    return
  }

  console.log('准备编辑节点:', selectedNode.value.id, selectedNode.value.topic)
  selectAndEditNode(selectedNode.value)
}

const confirmEdit = () => {
  if (!selectedNode.value || !jm.value) return

  jm.value.update_node(selectedNode.value.id, editForm.topic)

  selectedNode.value.testType = editForm.testType
  selectedNode.value.steps = editForm.steps ? editForm.steps.split('\n').filter(Boolean) : []
  selectedNode.value.expected = editForm.expected

  // 更新数据并触发事件
  const currentData = jm.value.get_data()
  const testCaseData = convertJsMindToTestCase(currentData)
  emit('data-change', testCaseData)

  showEditDialog.value = false
  ElMessage.success('节点更新成功')
}

const getCurrentData = (): TestCaseNode => {
  if (jm.value) {
    const currentData = jm.value.get_data()
    return convertJsMindToTestCase(currentData)
  }
  return props.data
}

// 监听数据变化
watch(() => props.data, (newData) => {
  console.log('数据变化监听器触发:', newData)

  // 如果有jsMind实例，销毁它
  if (jm.value) {
    try {
      jm.value.remove_event_listener()
      jm.value = null
      console.log('旧的jsMind实例已销毁')
    } catch (error) {
      console.log('销毁实例时出错:', error)
    }
  }

  // 延迟重新初始化
  setTimeout(() => {
    initJsMind()
  }, 50)
}, { deep: true })

// 暴露方法给父组件
defineExpose({
  getCurrentData,
  editSelectedNode,
  expandAll,
  collapseAll
})

onMounted(() => {
  // 动态加载 jsmind 样式和脚本
  if (typeof window !== 'undefined') {
    // 添加样式
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://cdn.jsdelivr.net/npm/jsmind@0.4.6/style/jsmind.css'
    document.head.appendChild(link)

    // 加载脚本
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/jsmind@0.4.6/js/jsmind.js'
    script.onload = () => {
      initJsMind()
    }
    document.head.appendChild(script)
  }
})

onUnmounted(() => {
  // 清理资源
  try {
    if (jm.value && typeof jm.value.remove_event_listener === 'function') {
      jm.value.remove_event_listener()
    } else if (jm.value && jm.value.mind) {
      // 尝试使用其他清理方法
      jm.value.mind.container.innerHTML = ''
    }
  } catch (error) {
    console.warn('JsMind cleanup error:', error)
  }
})
</script>

<style scoped>
.jsmind-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.jsmind-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 1000;
  background: white;
  padding: 8px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.jsmind-container {
  flex: 1;
  width: 100%;
  height: 100%;
  background-color: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.jsmind-node) {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.jsmind-selected) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  border: 2px solid #409eff;
}

/* 编辑对话框样式 */
:deep(.node-edit-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.node-edit-dialog .el-dialog__header) {
  padding: 0;
  margin: 0;
}

:deep(.node-edit-dialog .el-dialog__body) {
  padding: 0;
}

:deep(.node-edit-dialog .el-dialog__footer) {
  padding: 0;
  margin: 0;
}

/* 对话框头部 */
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-bottom: 1px solid #e6f7ff;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dialog-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.2;
}

.dialog-subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.4;
}

.close-btn {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #64748b;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #ffffff;
  border-color: #3b82f6;
  color: #3b82f6;
  transform: scale(1.05);
}

/* 对话框内容 */
.dialog-content {
  padding: 24px;
  max-height: 500px;
  overflow-y: auto;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.section-icon {
  width: 24px;
  height: 24px;
  background: #f1f5f9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  line-height: 1;
}

.form-item {
  margin: 0 !important;
}

/* 自定义输入框样式 */
:deep(.custom-input .el-input__wrapper) {
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  box-shadow: none;
  transition: all 0.3s ease;
  padding: 0 16px;
}

:deep(.custom-input .el-input__wrapper:hover) {
  border-color: #3b82f6;
}

:deep(.custom-input.is-focus .el-input__wrapper) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

:deep(.custom-input .el-input__inner) {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

/* 自定义选择框样式 */
:deep(.custom-select .el-select__wrapper) {
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  box-shadow: none;
  transition: all 0.3s ease;
  padding: 0 16px;
}

:deep(.custom-select .el-select__wrapper:hover) {
  border-color: #3b82f6;
}

:deep(.custom-select.is-focus .el-select__wrapper) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 选项样式 */
.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.option-item span {
  color: #374151;
  font-weight: 500;
}

/* 自定义文本域样式 */
:deep(.custom-textarea .el-textarea__inner) {
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  box-shadow: none;
  transition: all 0.3s ease;
  padding: 12px 16px;
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

:deep(.custom-textarea .el-textarea__inner:hover) {
  border-color: #3b82f6;
}

:deep(.custom-textarea.is-focus .el-textarea__inner) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px 24px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  border-color: #9ca3af;
  color: #374151;
  background: #f9fafb;
}

.confirm-btn {
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%);
  border: none;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.confirm-btn:hover {
  background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dialog-header {
    padding: 20px 20px 16px;
  }

  .header-content {
    gap: 12px;
  }

  .header-icon {
    width: 40px;
    height: 40px;
  }

  .dialog-title {
    font-size: 18px;
  }

  .dialog-subtitle {
    font-size: 13px;
  }

  .dialog-content {
    padding: 20px;
  }

  .dialog-footer {
    padding: 16px 20px 20px;
    flex-direction: column;
    gap: 8px;
  }

  .cancel-btn,
  .confirm-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>