import { createRouter, createWebHistory } from 'vue-router';
import ChatView from '../views/ChatView.vue';
import SettingsView from '../views/SettingsView.vue';
import ChatHistory from '../components/ChatHistory.vue'; // 导入 ChatHistory 组件

const routes = [
  {
    path: '/chat/:chatId?',
    name: 'chat',
    components: {
      default: ChatView,
      ChatHistory: ChatHistory
    },
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView
  },
  {
    path: '/',
    redirect: '/chat'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;