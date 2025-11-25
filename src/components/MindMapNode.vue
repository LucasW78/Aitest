<template>
  <div class="mind-map-node" :class="{ 'selected': isSelected }">
    <div class="node-content">
      <div
        class="node-body"
        :class="getNodeClass()"
        @click="handleClick"
        @contextmenu.prevent="showContextMenu"
      >
        <div class="node-icon">
          <el-icon v-if="node.children && node.children.length > 0">
            <Folder v-if="!isExpanded" />
            <FolderOpened v-else />
          </el-icon>
          <el-icon v-else>
            <Document />
          </el-icon>
        </div>

        <div class="node-text">
          <div class="node-label">{{ node.label }}</div>
          <div v-if="node.data?.testType" class="node-type">
            <el-tag :type="getTypeColor(node.data.testType)" size="small">
              {{ getTypeLabel(node.data.testType) }}
            </el-tag>
          </div>
        </div>

        <div v-if="node.children && node.children.length > 0" class="expand-btn" @click.stop="toggleExpand">
          <el-icon>
            <ArrowRight v-if="!isExpanded" />
            <ArrowDown v-else />
          </el-icon>
        </div>
      </div>

      <!-- 节点详细信息 -->
      <div v-if="node.data && showDetails" class="node-details">
        <div v-if="node.data.steps && node.data.steps.length > 0" class="detail-section">
          <strong>测试步骤：</strong>
          <ol>
            <li v-for="(step, index) in node.data.steps" :key="index">{{ step }}</li>
          </ol>
        </div>
        <div v-if="node.data.expected" class="detail-section">
          <strong>预期结果：</strong>
          <p>{{ node.data.expected }}</p>
        </div>
      </div>
    </div>

    <!-- 子节点 -->
    <div v-if="hasChildren && isExpanded" class="node-children">
      <div
        v-for="(child, index) in node.children"
        :key="child.id"
        class="child-node"
        :style="{ '--child-index': index }"
      >
        <MindMapNode
          :node="child"
          :editable="editable"
          :selected-node="selectedNode"
          @node-click="$emit('node-click', $event)"
          @node-edit="$emit('node-edit', $event)"
          @node-delete="$emit('node-delete', $event)"
          @node-add-child="$emit('node-add-child', $event)"
        />
      </div>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenuVisible"
      class="context-menu"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
      @click.stop
    >
      <div v-if="editable" class="context-menu-item" @click="editNode">
        <el-icon><Edit /></el-icon>
        编辑节点
      </div>
      <div v-if="editable" class="context-menu-item" @click="addChildNode">
        <el-icon><Plus /></el-icon>
        添加子节点
      </div>
      <div v-if="editable && node.id !== 'root'" class="context-menu-item danger" @click="deleteNode">
        <el-icon><Delete /></el-icon>
        删除节点
      </div>
      <div class="context-menu-item" @click="toggleDetails">
        <el-icon><View /></el-icon>
        {{ showDetails ? '隐藏' : '显示' }}详情
      </div>
      <div class="context-menu-divider"></div>
      <div class="context-menu-item" @click="hideContextMenu">
        <el-icon><Close /></el-icon>
        关闭
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { TestCaseNode } from '@/types'

interface Props {
  node: TestCaseNode
  editable?: boolean
  selectedNode?: string | null
}

interface Emits {
  (e: 'node-click', node: TestCaseNode): void
  (e: 'node-edit', node: TestCaseNode): void
  (e: 'node-delete', nodeId: string): void
  (e: 'node-add-child', node: TestCaseNode): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  selectedNode: null
})

const emit = defineEmits<Emits>()

// 响应式数据
const isExpanded = ref(true)
const showDetails = ref(false)
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)

// 计算属性
const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0
})

const isSelected = computed(() => {
  return props.selectedNode === props.node.id
})

// 方法
const getNodeClass = () => {
  const classes = ['node-body']

  if (isSelected.value) {
    classes.push('selected')
  }

  if (props.node.data?.testType) {
    classes.push(`test-type-${props.node.data.testType}`)
  }

  return classes.join(' ')
}

const getTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    positive: 'success',
    negative: 'danger',
    boundary: 'warning',
    ui: 'info',
    performance: 'primary'
  }
  return colorMap[type] || ''
}

const getTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    positive: '正向测试',
    negative: '负向测试',
    boundary: '边界测试',
    ui: 'UI测试',
    performance: '性能测试'
  }
  return labelMap[type] || type
}

const handleClick = () => {
  emit('node-click', props.node)
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const toggleDetails = () => {
  showDetails.value = !showDetails.value
  hideContextMenu()
}

const showContextMenu = (event: MouseEvent) => {
  event.preventDefault()
  contextMenuVisible.value = true
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
}

const hideContextMenu = () => {
  contextMenuVisible.value = false
}

const editNode = () => {
  emit('node-edit', props.node)
  hideContextMenu()
}

const addChildNode = () => {
  emit('node-add-child', props.node)
  hideContextMenu()
}

const deleteNode = () => {
  emit('node-delete', props.node.id)
  hideContextMenu()
}

const handleGlobalClick = () => {
  hideContextMenu()
}

onMounted(() => {
  document.addEventListener('click', handleGlobalClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleGlobalClick)
})
</script>

<style scoped>
.mind-map-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 8px 0;
  position: relative;
}

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.node-body {
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px 16px;
  min-width: 160px;
  max-width: 240px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-body:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.node-body.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.node-body.test-type-positive {
  border-left: 4px solid #67c23a;
}

.node-body.test-type-negative {
  border-left: 4px solid #f56c6c;
}

.node-body.test-type-boundary {
  border-left: 4px solid #e6a23c;
}

.node-body.test-type-ui {
  border-left: 4px solid #909399;
}

.node-body.test-type-performance {
  border-left: 4px solid #409eff;
}

.node-icon {
  color: #409eff;
  flex-shrink: 0;
}

.node-text {
  flex: 1;
  min-width: 0;
}

.node-label {
  font-weight: 500;
  font-size: 14px;
  color: #303133;
  word-break: break-word;
  line-height: 1.4;
}

.node-type {
  margin-top: 4px;
}

.expand-btn {
  position: absolute;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  background: #409eff;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.expand-btn:hover {
  background: #337ecc;
}

.node-details {
  margin-top: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px;
  font-size: 12px;
  max-width: 300px;
}

.detail-section {
  margin-bottom: 8px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section strong {
  color: #495057;
}

.detail-section ol {
  margin: 4px 0 0 16px;
  padding: 0;
}

.detail-section li {
  margin-bottom: 2px;
  color: #6c757d;
}

.detail-section p {
  margin: 4px 0 0 0;
  color: #6c757d;
}

.node-children {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 16px;
  position: relative;
}

.child-node {
  position: relative;
  margin: 4px 0;
}

.child-node::before {
  content: '';
  position: absolute;
  top: -20px;
  left: 50%;
  width: 2px;
  height: 20px;
  background-color: #d1d5db;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 120px;
  padding: 4px 0;
}

.context-menu-item {
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #303133;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background-color: #f5f7fa;
}

.context-menu-item.danger {
  color: #f56c6c;
}

.context-menu-item.danger:hover {
  background-color: #fef0f0;
}

.context-menu-divider {
  height: 1px;
  background-color: #e4e7ed;
  margin: 4px 0;
}
</style>