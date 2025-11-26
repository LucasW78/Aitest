<template>
  <div class="jsmind-viewer">
    <div class="jsmind-toolbar">
      <el-button-group size="small">
        <el-button @click="zoomIn" :disabled="zoomLevel >= 2">
          <el-icon><ZoomIn /></el-icon>
        </el-button>
        <el-button @click="zoomOut" :disabled="zoomLevel <= 0.3">
          <el-icon><ZoomOut /></el-icon>
        </el-button>
        <el-button @click="resetZoom">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
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

      <el-button-group size="small" style="margin-left: 8px" v-if="editable">
        <el-button type="primary" @click="addSelectedNode">
          <el-icon><Plus /></el-icon>
          添加子节点
        </el-button>
        <el-button type="warning" @click="removeSelectedNode">
          <el-icon><Delete /></el-icon>
          删除节点
        </el-button>
      </el-button-group>
    </div>

    <div id="jsmind_container" class="jsmind-container"></div>

    <!-- 节点编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑节点" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="节点名称：">
          <el-input v-model="editForm.topic" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="测试类型：" v-if="isTestCaseNode">
          <el-select v-model="editForm.testType" placeholder="请选择测试类型" style="width: 100%">
            <el-option label="正向测试" value="positive" />
            <el-option label="负向测试" value="negative" />
            <el-option label="边界测试" value="boundary" />
            <el-option label="UI测试" value="ui" />
            <el-option label="性能测试" value="performance" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试步骤：" v-if="isTestCaseNode">
          <el-input
            v-model="editForm.steps"
            type="textarea"
            :rows="3"
            placeholder="请输入测试步骤，每行一个步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果：" v-if="isTestCaseNode">
          <el-input
            v-model="editForm.expected"
            type="textarea"
            :rows="2"
            placeholder="请输入预期结果"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmEdit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
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
const convertTestCaseToJsMind = (testCaseData: TestCaseNode) => {
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

// 初始化 jsmind
const initJsMind = async () => {
  await nextTick()

  if (typeof window !== 'undefined' && window.jsMind) {
    const options = {
      container: 'jsmind_container',
      theme: 'primary',
      mode: 'full',
      support_html: true,
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

    const mindData = convertTestCaseToJsMind(props.data)
    jm.value.show(mindData)

    // 绑定事件
    jm.value.add_event_listener((type: string, data: any) => {
      if (type === 'select_node') {
        selectedNode.value = data.node
        const testCaseNode = convertJsMindToTestCase({ data: data.node })
        emit('node-click', testCaseNode)
      }
    })

    // 默认展开所有节点
    setTimeout(() => {
      expandAll()
    }, 100)
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
    jm.value.view.zoomIn(0)
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
  if (!jm.value || !selectedNode.value) {
    ElMessage.warning('请先选择一个节点')
    return
  }

  const nodeId = 'node_' + Date.now()
  const newNode = {
    id: nodeId,
    topic: '新测试用例',
    testType: 'positive',
    steps: ['步骤1', '步骤2'],
    expected: '预期结果'
  }

  jm.value.add_node(selectedNode.value.id, newNode)
  ElMessage.success('节点添加成功')
}

const removeSelectedNode = () => {
  if (!jm.value || !selectedNode.value) {
    ElMessage.warning('请先选择要删除的节点')
    return
  }

  if (selectedNode.value.isroot) {
    ElMessage.error('不能删除根节点')
    return
  }

  jm.value.remove_node(selectedNode.value.id)
  selectedNode.value = null
  ElMessage.success('节点删除成功')
}

const editSelectedNode = () => {
  if (!selectedNode.value) {
    ElMessage.warning('请先选择要编辑的节点')
    return
  }

  editForm.topic = selectedNode.value.topic
  editForm.testType = selectedNode.value.testType || ''
  editForm.steps = selectedNode.value.steps ? selectedNode.value.steps.join('\n') : ''
  editForm.expected = selectedNode.value.expected || ''
  showEditDialog.value = true
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
watch(() => props.data, () => {
  if (jm.value) {
    const mindData = convertTestCaseToJsMind(props.data)
    jm.value.show(mindData)
  }
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
  if (jm.value) {
    jm.value.remove_event_listener()
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
</style>