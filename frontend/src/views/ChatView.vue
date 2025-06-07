<template>
  <div class="chat-container">
    <div class="message-list">
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message-bubble', message.role]"
      >
        <div class="message-avatar">
          <el-avatar :icon="message.role === 'user' ? 'User' : 'ChatRound'" />
        </div>
        <div class="message-content-wrapper">
          <div class="message-role">{{ message.role === 'user' ? '你' : 'AI助手' }}</div>
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入消息..."
        :autosize="{ minRows: 1, maxRows: 4 }"
        resize="none"
        @keyup.enter.native="sendMessage"
      />
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
import axios from 'axios';

export default {
  name: 'ChatView',
  data() {
    return {
      messages: [],
      inputMessage: '',
      isLoading: false
    };
  },
  methods: {
    async sendMessage() {
      if (!this.inputMessage.trim()) return;
      
      this.isLoading = true;
      const userMessage = { role: 'user', content: this.inputMessage };
      this.messages.push(userMessage);
      
      try {
        const response = await axios.post('/v1/chat/completions', {
          messages: this.messages,
          model: 'default'
        });
        
        this.messages.push({
          role: 'assistant',
          content: response.data.choices[0].message.content
        });
      } catch (error) {
        console.error('请求失败:', error);
        this.$message.error('发送消息失败');
      } finally {
        this.isLoading = false;
        this.inputMessage = '';
      }
    }
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
  background: #f8f9fa;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
}

.message-bubble {
  display: flex;
  margin-bottom: 24px;
  max-width: 80%;
  transition: all 0.3s ease;
}

.message-bubble.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-bubble.assistant {
  margin-right: auto;
}

.message-content {
  display: inline-block;
  padding: 10px 15px;
  border-radius: 8px;
  background: #f5f7fa;
}

.message.user .message-content {
  background: #409EFF;
  color: white;
}

.input-area {
  padding: 20px;
  border-top: 1px solid #e6e6e6;
}

.el-button {
  margin-top: 10px;
}
</style>