<template>
  <div class="home-container">
    <!-- 头部 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <h1>AI用例生成平台</h1>
        </div>
        <div class="user-info">
          <el-avatar :size="40" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          <span class="username">管理员</span>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- Tab导航 -->
      <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick" class="main-tabs">
        <el-tab-pane label="文档管理" name="documents" lazy>
          <DocumentManagement />
        </el-tab-pane>
        <el-tab-pane label="用例设计" name="test-design" lazy>
          <TestCaseDesign />
        </el-tab-pane>
      </el-tabs>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DocumentManagement from './DocumentManagement.vue'
import TestCaseDesign from './TestCaseDesign.vue'

const router = useRouter()
const activeTab = ref('documents')

const handleTabClick = (tab: any) => {
  const routeMap: Record<string, string> = {
    'documents': '/documents',
    'test-design': '/test-design'
  }

  if (routeMap[tab.name]) {
    router.push(routeMap[tab.name])
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.main-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

:deep(.el-tabs__header) {
  margin: 0;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

:deep(.el-tabs__content) {
  padding: 24px;
  min-height: 600px;
}
</style>