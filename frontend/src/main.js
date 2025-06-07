// 从 'vue' 导入 'createApp' 函数，用于创建 Vue 应用实例
import { createApp } from 'vue'
// 导入根组件 'App.vue'
import App from './App.vue'
// 导入 Element Plus UI 库
import ElementPlus from 'element-plus'
// 导入 Element Plus 的默认样式
import 'element-plus/dist/index.css'
// 导入 Vue Router 实例
import router from './router'

// 创建 Vue 应用实例，并将根组件 App 传入
const app = createApp(App)

// 全局注册 Element Plus 插件
app.use(ElementPlus)
// 全局注册 Vue Router 插件
app.use(router)

// 将应用挂载到 DOM 中 id 为 'app' 的元素上
app.mount('#app')