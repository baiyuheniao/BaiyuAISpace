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

<script setup>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useRoute } from 'vue-router';

const route = useRoute();
const messages = ref([]);
const inputMessage = ref('');
const isLoading = ref(false);
const activeChatId = ref(null);

// 从 localStorage 加载所有聊天数据
const loadAllChats = () => {
  const storedChats = localStorage.getItem('chatList');
  return storedChats ? JSON.parse(storedChats) : [];
};

// 保存所有聊天数据到 localStorage
const saveAllChats = (chats) => {
  localStorage.setItem('chatList', JSON.stringify(chats));
};

// 根据 activeChatId 加载当前对话的消息
const loadMessagesForActiveChat = () => {
  const allChats = loadAllChats();
  const currentChat = allChats.find(chat => chat.id === activeChatId.value);
  messages.value = currentChat ? currentChat.messages : [];
};

// 更新当前对话的消息并保存
const updateMessagesAndSave = () => {
  const allChats = loadAllChats();
  const chatIndex = allChats.findIndex(chat => chat.id === activeChatId.value);
  if (chatIndex !== -1) {
    allChats[chatIndex].messages = messages.value;
    saveAllChats(allChats);
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;
  if (!activeChatId.value) {
    ElMessage.warning('请先选择或新建一个对话');
    return;
  }

  isLoading.value = true;
  const userMessage = { role: 'user', content: inputMessage.value };
  messages.value.push(userMessage);
  updateMessagesAndSave(); // 保存用户消息
  inputMessage.value = '';

  try {
    const response = await axios.post('/v1/chat/completions', {
      messages: messages.value,
      model: 'default'
    });

    messages.value.push({
      role: 'assistant',
      content: response.data.choices[0].message.content
    });
    updateMessagesAndSave(); // 保存 AI 助手的回复
  } catch (error) {
    console.error('请求失败:', error);
    ElMessage.error('发送消息失败');
  } finally {
    isLoading.value = false;
  }
};

// 监听路由参数变化，更新 activeChatId
watch(() => route.params.chatId, (newChatId) => {
  if (newChatId) {
    activeChatId.value = newChatId;
    loadMessagesForActiveChat();
  }
}, { immediate: true }); // 立即执行一次，确保初始加载

// 监听 activeChatId 变化，加载对应消息
watch(activeChatId, (newId) => {
  if (newId) {
    loadMessagesForActiveChat();
  }
});

// 初始加载时，如果路由中没有chatId，则尝试从localStorage获取第一个对话的ID
onMounted(() => {
  if (!route.params.chatId) {
    const allChats = loadAllChats();
    if (allChats.length > 0) {
      activeChatId.value = allChats[0].id;
      loadMessagesForActiveChat();
    }
  }
});
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


</style>