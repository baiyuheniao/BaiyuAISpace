<template>
  <div class="chat-history">
    <h3>历史对话</h3>
    <el-button type="primary" :icon="Plus" @click="newChat" class="new-chat-button">新建对话</el-button>
    <el-menu
      :default-active="activeChatId"
      class="chat-history-menu"
      @select="handleSelectChat"
    >
      <el-menu-item v-for="chat in chatList" :key="chat.id" :index="chat.id">
        <el-icon><ChatDotRound /></el-icon>
        <span class="chat-title">{{ chat.name }}</span>
        <div class="chat-actions">
          <el-button :icon="Edit" circle size="small" @click.stop="renameChat(chat)" />
          <el-button :icon="Delete" circle size="small" @click.stop="deleteChat(chat)" />
        </div>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Star, Delete, Edit, ChatDotRound } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';

const chatList = ref([]);
const activeChatId = ref(null);
const router = useRouter();

// 从本地存储加载聊天列表
const loadChats = () => {
  const storedChats = localStorage.getItem('chatList');
  if (storedChats) {
    chatList.value = JSON.parse(storedChats);
    if (chatList.value.length > 0) {
      activeChatId.value = chatList.value[0].id; // 默认选中第一个对话
    }
  }
};

// 保存聊天列表到本地存储
const saveChats = () => {
  localStorage.setItem('chatList', JSON.stringify(chatList.value));
};

const handleNewChat = () => {
  const newChat = {
    id: Date.now().toString(),
    title: `新对话 ${chatList.value.length + 1}`,
    messages: [],
    favorite: false,
  };
  chatList.value.unshift(newChat);
  saveChats();
  activeChatId.value = newChat.id;
  router.push({ name: 'chat', params: { chatId: newChat.id } });
};

const handleSelectChat = (chatId) => {
  activeChatId.value = chatId;
  router.push({ name: 'chat', params: { chatId: chatId } });
};

// 重命名对话
const renameChat = async (chat) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的对话名称', '重命名对话', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: chat.name,
    });
    if (value && value.trim() !== '') {
      chat.name = value.trim();
      saveChats();
      ElMessage.success('重命名成功');
    } else {
      ElMessage.warning('对话名称不能为空');
    }
  } catch (error) {
    // 用户取消或输入为空
    if (error === 'cancel') {
      ElMessage.info('取消重命名');
    } else {
      console.error('重命名失败:', error);
      ElMessage.error('重命名失败');
    }
  }
};

// 删除对话
const deleteChat = async (chat) => {
  try {
    await ElMessageBox.confirm(`确定要删除对话 "${chat.name}" 吗？`, '删除对话', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    chatList.value = chatList.value.filter(c => c.id !== chat.id);
    saveChats();
    if (activeChatId.value === chat.id) {
      activeChatId.value = chatList.value.length > 0 ? chatList.value[0].id : null;
    }
    ElMessage.success('删除成功');
  } catch (error) {
    if (error === 'cancel') {
      ElMessage.info('取消删除');
    } else {
      console.error('删除失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 初始加载
onMounted(() => {
  loadChats();
  if (chatList.value.length === 0) {
    newChat(); // 如果没有对话，则新建一个
  }
});

// 监听 chatList 变化，自动保存
watch(chatList, saveChats, { deep: true });

// 暴露给父组件或 ChatView 使用
defineExpose({
  activeChatId,
  chatList,
});
</script>

<style scoped>
.chat-history {
  padding: 16px;
}

.chat-history h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 1.1rem;
  color: #333;
}

.new-chat-button {
  width: 100%;
  margin-bottom: 16px;
}

.chat-history-menu {
  border-right: none;
}

.chat-history-menu .el-menu-item {
  border-radius: 8px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between; /* 使内容和操作按钮两端对齐 */
}

.chat-history-menu .el-menu-item .chat-title {
  flex-grow: 1; /* 标题占据剩余空间 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-history-menu .el-menu-item .chat-actions {
  display: none; /* 默认隐藏操作按钮 */
}

.chat-history-menu .el-menu-item:hover .chat-actions {
  display: flex; /* 鼠标悬停时显示操作按钮 */
}

.chat-history-menu .el-menu-item.is-active {
  background-color: var(--primary-color);
  color: white;
}

.chat-history-menu .el-menu-item.is-active .el-icon {
  color: white;
}

.chat-history-menu .el-menu-item.is-active .chat-actions .el-button {
  color: white; /* 激活状态下按钮颜色为白色 */
  background-color: transparent; /* 激活状态下按钮背景透明 */
  border: none;
}
</style>