<template>
  <transition name="sidebar-slide">
    <div
      class="sidebar-nav"
      :class="{ expanded: isHovered }"
      @mouseenter="isHovered = true"
      @mouseleave="isHovered = false"
    >
      <div class="nav-btn" :class="{ active: isChat }" @click="goChat">
        <el-icon><ChatDotRound /></el-icon>
        <span v-if="isHovered" class="nav-label">对话</span>
      </div>
      <div class="nav-btn" :class="{ active: isSettings }" @click="goSettings">
        <el-icon><Setting /></el-icon>
        <span v-if="isHovered" class="nav-label">设置</span>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChatDotRound, Setting } from '@element-plus/icons-vue'

const isHovered = ref(false)
const router = useRouter()
const route = useRoute()

const isChat = computed(() => route.path.startsWith('/chat'))
const isSettings = computed(() => route.path.startsWith('/settings'))

function goChat() {
  router.push('/chat')
}
function goSettings() {
  router.push('/settings')
}

watch(isHovered, (val) => {
  window.dispatchEvent(new CustomEvent('sidebar-nav-toggle', { detail: val }))
})
</script>

<style scoped>
.sidebar-nav {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  height: 100vh;
  width: 56px;
  background: #fff;
  border-right: 1px solid #e6e6e6;
  box-shadow: 2px 0 8px 0 rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 48px;
  transition: width 0.3s cubic-bezier(.4,0,.2,1);
}
.sidebar-nav.expanded {
  width: 160px;
}
.nav-btn {
  width: 40px;
  height: 40px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, width 0.3s;
  color: #909399;
  font-size: 22px;
  position: relative;
}
.sidebar-nav.expanded .nav-btn {
  width: 120px;
  justify-content: flex-start;
  padding-left: 16px;
}
.nav-btn.active {
  background: #ecf5ff;
  color: #409EFF;
}
.nav-btn:hover {
  background: #f5f7fa;
  color: #409EFF;
}
.nav-label {
  margin-left: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.2s;
}
.sidebar-slide-enter-active, .sidebar-slide-leave-active {
  transition: width 0.3s cubic-bezier(.4,0,.2,1);
}
</style> 