<template>
  <!-- 聊天容器 -->
  <div class="chat-container">
    <!-- 消息列表区域 -->
    <div class="message-list">
      <!-- 遍历消息数组，显示每条消息 -->
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message-bubble', message.role]"
      >
        <!-- 消息头像 -->
        <div class="message-avatar">
          <el-avatar :icon="message.role === 'user' ? 'User' : 'ChatRound'" />
        </div>
        <!-- 消息内容包装器 -->
        <div class="message-content-wrapper">
          <!-- 消息角色显示 -->
          <div class="message-role">{{ message.role === 'user' ? '你' : 'AI助手' }}</div>
          <!-- 消息实际内容 -->
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-area">
      <!-- 文本输入框 -->
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入消息..."
        :autosize="{ minRows: 1, maxRows: 4 }"
        resize="none"
        @keyup.enter.native="sendMessage"
      />
      <!-- 发送按钮 -->
      <el-button 
        type="primary" 
        @click="sendMessage"
        :loading="isLoading"
        class="send-button"
      >
        <el-icon><Promotion /></el-icon>
        <span>发送</span>
      </el-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'; // 导入 axios 用于 HTTP 请求

export default {
  name: 'ChatView', // 组件名称
  data() { // 组件数据
    return {
      messages: [], // 存储聊天消息的数组
      inputMessage: '', // 输入框中的消息内容
      isLoading: false // 发送按钮的加载状态
    };
  },
  methods: { // 组件方法
    async sendMessage() { // 发送消息方法
      if (!this.inputMessage.trim()) return; // 如果输入为空，则不发送
      
      this.isLoading = true; // 设置加载状态为 true
      const userMessage = { role: 'user', content: this.inputMessage }; // 创建用户消息对象
      this.messages.push(userMessage); // 将用户消息添加到消息列表
      
      try {
        // 发送 POST 请求到后端 API
        const response = await axios.post('/v1/chat/completions', {
          messages: this.messages, // 发送当前所有消息
          model: 'default' // 使用默认模型
        });
        
        // 将 AI 助手的回复添加到消息列表
        this.messages.push({
          role: 'assistant',
          content: response.data.choices[0].message.content
        });
      } catch (error) {
        console.error('请求失败:', error); // 打印错误信息
        this.$message.error('发送消息失败'); // 显示错误提示
      } finally {
        this.isLoading = false; // 无论成功或失败，都将加载状态设置为 false
        this.inputMessage = ''; // 清空输入框
      }
    }
  }
};
</script>

<style scoped>
/* 聊天容器样式 */
.chat-container {
  display: flex; /* 弹性布局 */
  flex-direction: column; /* 垂直方向排列 */
  height: 100%; /* 高度占满父容器 */
  padding: 16px; /* 内边距 */
  background: #f8f9fa; /* 背景色 */
}

/* 消息列表样式 */
.message-list {
  flex: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 垂直滚动 */
  padding: 16px; /* 内边距 */
  scroll-behavior: smooth; /* 平滑滚动 */
}

/* 消息气泡通用样式 */
.message-bubble {
  display: flex; /* 弹性布局 */
  margin-bottom: 24px; /* 下外边距 */
  max-width: 80%; /* 最大宽度 */
  transition: all 0.3s ease; /* 过渡效果 */
}

/* 用户消息气泡样式 */
.message-bubble.user {
  margin-left: auto; /* 靠右对齐 */
  flex-direction: row-reverse; /* 反向排列，使头像在右侧 */
}

/* AI 助手消息气泡样式 */
.message-bubble.assistant {
  margin-right: auto; /* 靠左对齐 */
}

/* 消息内容样式 */
.message-content {
  display: inline-block; /* 行内块级元素 */
  padding: 10px 15px; /* 内边距 */
  border-radius: 8px; /* 圆角 */
  background: #f5f7fa; /* 背景色 */
}

/* 用户消息内容样式 */
.message.user .message-content {
  background: #409EFF; /* 背景蓝色 */
  color: white; /* 文本白色 */
}

/* 输入区域样式 */
.input-area {
  padding: 20px; /* 内边距 */
  border-top: 1px solid #e6e6e6; /* 上边框 */
}

/* 按钮样式 */
.el-button {
  margin-top: 10px; /* 上外边距 */
}
</style>