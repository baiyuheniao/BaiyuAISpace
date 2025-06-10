<template>
  <!-- 应用程序的根容器 -->
  <div id="app">
    <!-- 整体布局容器 -->
    <el-container class="app-container">
      <!-- 头部区域 -->
      <el-header class="app-header">
        <!-- 头部内容容器 -->
        <div class="header-content">
          <!-- 应用标题 -->
          <h1 class="app-title">BaiyuAISpace</h1>
          <!-- 导航区域 -->
          <div class="app-nav">
            <!-- 导航按钮，遍历 navLinks 数组生成 -->
            <!-- 导航按钮，根据当前路由路径判断是否激活，点击时跳转到对应路由 -->
            <el-button 
              type="link" 
              v-for="link in navLinks" 
              :key="link.path"
              :class="{ active: $route.path === link.path }"
              @click="$router.push(link.path)"
            >
              {{ link.title }}
            </el-button>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容区域容器 -->
      <el-container>
        <!-- 主内容区域 -->
        <el-main class="app-main">
          <!-- 路由视图，显示当前路由对应的组件 -->
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App', // 组件名称
  data() { // 组件数据
    return {
      // 导航链接数组
      navLinks: [
        { path: '/chat', title: '对话' }, // 对话页面链接
        { path: '/settings', title: '设置' } // 设置页面链接
      ]
    }
  }
}
</script>

<style>
/* CSS 变量定义 */
:root {
  --primary-color: #3a86ff; /* 主题色 */
  --bg-color: #f8f9fa; /* 背景色 */
  --text-color: #212529; /* 文本颜色 */
  --border-color: #e9ecef; /* 边框颜色 */
  --header-height: 64px; /* 头部高度 */
}

/* 应用根样式 */
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; /* 字体栈 */
  -webkit-font-smoothing: antialiased; /* 字体抗锯齿 */
  -moz-osx-font-smoothing: grayscale; /* 字体灰度抗锯齿 */
  color: var(--text-color); /* 文本颜色 */
  height: 100vh; /* 高度占满视口 */
  background: var(--bg-color); /* 背景色 */
}

/* 容器样式 */
.app-container {
  height: 100%; /* 高度占满父容器 */
}

/* 头部样式 */
.app-header {
  height: var(--header-height) !important; /* 头部高度 */
  background: white; /* 背景白色 */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  z-index: 10; /* 层级 */
}

/* 头部内容样式 */
.header-content {
  display: flex; /* 弹性布局 */
  align-items: center; /* 垂直居中 */
  justify-content: space-between; /* 水平两端对齐 */
  max-width: 1200px; /* 最大宽度 */
  margin: 0 auto; /* 水平居中 */
  padding: 0 24px; /* 内边距 */
  height: 100%; /* 高度占满父容器 */
}

/* 应用标题样式 */
.app-title {
  font-size: 1.25rem; /* 字体大小 */
  font-weight: 600; /* 字体粗细 */
  margin: 0; /* 外边距 */
  color: var(--text-color); /* 文本颜色 */
}

/* 导航按钮样式 */
.app-nav .el-button {
  margin-left: 16px; /* 左外边距 */
  color: var(--text-color); /* 文本颜色 */
  font-weight: 500; /* 字体粗细 */
}

/* 激活状态的导航按钮样式 */
.app-nav .el-button.active {
  color: var(--primary-color); /* 激活时文本颜色 */
}

/* 主内容区域样式 */
.app-main {
  padding: 24px; /* 内边距 */
  max-width: 1200px; /* 最大宽度 */
  margin: 0 auto; /* 水平居中 */
}
</style>