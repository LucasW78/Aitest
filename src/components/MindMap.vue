<template>
  <div class="mind-map" ref="mindMapContainer">
    <div class="mind-map-toolbar">
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
        <el-button type="primary" @click="addNode">
          <el-icon><Plus /></el-icon>
          添加节点
        </el-button>
      </el-button-group>
    </div>

    <div class="mind-map-content" :style="{ transform: `scale(${zoomLevel})` }">
      <MindMapNode
        v-for="node in nodes"
        :key="node.id"
        :node="node"
        :editable="editable"
        :selected-node="selectedNode"
        @node-click="handleNodeClick"
        @node-edit="handleNodeEdit"
        @node-delete="handleNodeDelete"
        @node-add-child="handleNodeAddChild"
      />
    </div>

    <!-- 节点编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑节点" width="500px">
      <el-form :model="editForm">
        <el-form-item label="节点名称：">
          <el-input v-model="editForm.label" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="测试类型：">
          <el-select v-model="editForm.testType" placeholder="请选择测试类型" style="width: 100%">
            <el-option label="正向测试" value="positive" />
            <el-option label="负向测试" value="negative" />
            <el-option label="边界测试" value="boundary" />
            <el-option label="UI测试" value="ui" />
            <el-option label="性能测试" value="performance" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试步骤：">
          <el-input
            v-model="editForm.steps"
            type="textarea"
            :rows="3"
            placeholder="请输入测试步骤，每行一个步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果：">
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
import { ref, reactive, computed, watch, onMounted } from 'vue'
import type { TestCaseNode } from '@/types'

interface Props {
  data: TestCaseNode
  editable?: boolean
}

interface Emits {
  (e: 'node-click', node: TestCaseNode): void
  (e: 'node-edit', node: TestCaseNode): void
  (e: 'data-change', data: TestCaseNode): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const mindMapContainer = ref<HTMLElement>()
const zoomLevel = ref(1)
const selectedNode = ref<string | null>(null)
const nodes = computed(() => [props.data])
const showEditDialog = ref(false)
const currentEditNode = ref<TestCaseNode | null>(null)

const editForm = reactive({
  label: '',
  testType: '',
  steps: '',
  expected: ''
})

// 监听数据变化
watch(() => props.data, () => {
  selectedNode.value = null
}, { deep: true })

// 方法
const handleNodeClick = (node: TestCaseNode) => {
  selectedNode.value = node.id
  emit('node-click', node)
}

const handleNodeEdit = (node: TestCaseNode) => {
  currentEditNode.value = node
  editForm.label = node.label
  editForm.testType = node.data?.testType || ''
  editForm.steps = node.data?.steps ? node.data.steps.join('\n') : ''
  editForm.expected = node.data?.expected || ''
  showEditDialog.value = true
}

const confirmEdit = () => {
  if (currentEditNode.value) {
    currentEditNode.value.label = editForm.label
    currentEditNode.value.data = {
      ...currentEditNode.value.data,
      testType: editForm.testType,
      steps: editForm.steps ? editForm.steps.split('\n').filter(Boolean) : [],
      expected: editForm.expected
    }
    emit('node-edit', currentEditNode.value)
    emit('data-change', props.data)
  }
  showEditDialog.value = false
}

const handleNodeDelete = (nodeId: string) => {
  const deleteNode = (node: TestCaseNode): TestCaseNode | null => {
    if (node.id === nodeId) return null
    if (node.children) {
      node.children = node.children.map(child => deleteNode(child)).filter(Boolean) as TestCaseNode[]
    }
    return node
  }

  const updatedData = deleteNode(props.data)
  if (updatedData) {
    emit('data-change', updatedData)
  }
}

const handleNodeAddChild = (parentNode: TestCaseNode) => {
  const newChild: TestCaseNode = {
    id: `node_${Date.now()}`,
    label: '新测试用例',
    data: {
      testType: 'positive',
      steps: ['步骤1', '步骤2'],
      expected: '预期结果'
    }
  }

  const addChild = (node: TestCaseNode): TestCaseNode => {
    if (node.id === parentNode.id) {
      return {
        ...node,
        children: [...(node.children || []), newChild]
      }
    }
    if (node.children) {
      node.children = node.children.map(child => addChild(child))
    }
    return node
  }

  const updatedData = addChild(props.data)
  emit('data-change', updatedData)
}

const addNode = () => {
  if (!props.data.children) {
    props.data.children = []
  }

  const newNode: TestCaseNode = {
    id: `node_${Date.now()}`,
    label: '新测试场景',
    children: []
  }

  props.data.children.push(newNode)
  emit('data-change', props.data)
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 0.2, 2)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 0.2, 0.3)
}

const resetZoom = () => {
  zoomLevel.value = 1
}

const expandAll = () => {
  const expand = (node: TestCaseNode) => {
    node._expanded = true
    if (node.children) {
      node.children.forEach(expand)
    }
  }
  expand(props.data)
  emit('data-change', props.data)
}

const collapseAll = () => {
  const collapse = (node: TestCaseNode) => {
    node._expanded = false
    if (node.children) {
      node.children.forEach(collapse)
    }
  }
  collapse(props.data)
  emit('data-change', props.data)
}

onMounted(() => {
  // 默认展开所有节点
  expandAll()
})
</script>

<style scoped>
.mind-map {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: #fafafa;
  border-radius: 8px;
}

.mind-map-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 1000;
  background: white;
  padding: 8px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mind-map-content {
  padding: 80px 20px 20px;
  transition: transform 0.3s ease;
  transform-origin: center center;
  min-height: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

:deep(.el-dialog__body) {
  padding: 20px;
}
</style>