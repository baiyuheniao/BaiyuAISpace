<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">BaiyuAISpace</h1>
          <div class="app-nav">
            <el-button 
              type="text" 
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
      
      <el-container>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      navLinks: [
        { path: '/chat', title: '对话' },
        { path: '/settings', title: '设置' }
      ]
    }
  }
}
</script>

<style>
:root {
  --primary-color: #3a86ff;
  --bg-color: #f8f9fa;
  --text-color: #212529;
  --border-color: #e9ecef;
  --header-height: 64px;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-color);
  height: 100vh;
  background: var(--bg-color);
}

.app-container {
  height: 100%;
}

.app-header {
  height: var(--header-height) !important;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
}

.app-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.app-nav .el-button {
  margin-left: 16px;
  color: var(--text-color);
  font-weight: 500;
}

.app-nav .el-button.active {
  color: var(--primary-color);
}

.app-main {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
//你写注释了吗？
=======
</style>
>>>>>>> f4e6f5ba9052c9714820f988941221d706486134
