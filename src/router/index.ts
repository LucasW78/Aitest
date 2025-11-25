import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/documents',
      name: 'documents',
      component: () => import('@/views/DocumentManagement.vue')
    },
    {
      path: '/test-design',
      name: 'test-design',
      component: () => import('@/views/TestCaseDesign.vue')
    }
  ]
})

export default router