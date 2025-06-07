// 从 'vue-router' 导入 'createRouter' 和 'createWebHistory' 函数
import { createRouter, createWebHistory } from 'vue-router'
// 导入聊天视图组件
import ChatView from '../views/ChatView.vue'
// 导入设置视图组件
import SettingsView from '../views/SettingsView.vue'

// 定义路由配置数组
const routes = [
  {
    path: '/chat', // 聊天页面的路径
    name: 'chat', // 聊天页面的名称
    component: ChatView // 对应的组件
  },
  {
    path: '/settings', // 设置页面的路径
    name: 'settings', // 设置页面的名称
    component: SettingsView // 对应的组件
  },
  {
    path: '/', // 根路径
    redirect: '/chat' // 重定向到聊天页面
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 History 模式
  routes // 路由配置
})

// 导出路由实例
export default router