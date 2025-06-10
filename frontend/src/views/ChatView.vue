<template>
  <!-- 聊天主容器 -->
  <div class="chat-main-container">
    <!-- 历史记录侧边栏 -->
    <div class="history-sidebar" :class="{ 'collapsed': historyCollapsed }">
      <div class="sidebar-header">
        <h3>聊天历史</h3>
        <el-button type="primary" size="small" @click="createNewChat">
          <el-icon><Plus /></el-icon>
          新对话
        </el-button>
        <el-button type="text" class="collapse-button" @click="historyCollapsed = !historyCollapsed">
          <el-icon><ArrowLeft v-if="!historyCollapsed" /><ArrowRight v-else /></el-icon>
        </el-button>
      </div>
      
      <!-- 历史记录选项卡 -->
      <el-tabs v-model="activeHistoryTab" class="history-tabs">
        <el-tab-pane label="全部" name="all">
          <div class="history-list">
            <div 
              v-for="history in chatHistories" 
              :key="history.id"
              :class="['history-item', { 'active': currentHistoryId === history.id }]"
              @click="switchHistory(history.id)"
            >
              <div class="history-title-wrapper">
                <el-tooltip :content="history.title" placement="top" :disabled="history.title.length < 15">
                  <span class="history-title">{{ history.title }}</span>
                </el-tooltip>
                <span class="history-date">{{ formatDate(history.updated_at) }}</span>
              </div>
              <div class="history-actions">
                <el-button type="text" size="small" @click.stop="toggleFavorite(history.id)">
                  <el-icon><Star v-if="history.is_favorite" style="color: #f0c400;" /><Star v-else /></el-icon>
                </el-button>
                <el-dropdown @command="(cmd) => handleHistoryAction(cmd, history.id)" trigger="click" @click.stop>
                  <el-button type="text" size="small">
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="rename">重命名</el-dropdown-item>
                      <el-dropdown-item command="delete" style="color: #f56c6c;">删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="收藏" name="favorites">
          <div class="history-list">
            <div 
              v-for="history in favoriteHistories" 
              :key="history.id"
              :class="['history-item', { 'active': currentHistoryId === history.id }]"
              @click="switchHistory(history.id)"
            >
              <div class="history-title-wrapper">
                <el-tooltip :content="history.title" placement="top" :disabled="history.title.length < 15">
                  <span class="history-title">{{ history.title }}</span>
                </el-tooltip>
                <span class="history-date">{{ formatDate(history.updated_at) }}</span>
              </div>
              <div class="history-actions">
                <el-button type="text" size="small" @click.stop="toggleFavorite(history.id)">
                  <el-icon><Star style="color: #f0c400;" /></el-icon>
                </el-button>
                <el-dropdown @command="(cmd) => handleHistoryAction(cmd, history.id)" trigger="click" @click.stop>
                  <el-button type="text" size="small">
                    <el-icon><More /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="rename">重命名</el-dropdown-item>
                      <el-dropdown-item command="delete" style="color: #f56c6c;">删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 聊天容器 -->
    <div class="chat-container">
      <!-- 消息列表区域 -->
      <div class="message-list" ref="messageList">
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
    
    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名对话" width="30%">
      <el-input v-model="newHistoryTitle" placeholder="请输入新的对话名称" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'; // 导入 axios 用于 HTTP 请求
import { Plus, ArrowLeft, ArrowRight, Star, More } from '@element-plus/icons-vue'; // 导入图标

export default {
  name: 'ChatView', // 组件名称
  components: {
    Plus,
    ArrowLeft,
    ArrowRight,
    Star,
    More
  },
  data() { // 组件数据
    return {
      messages: [], // 存储聊天消息的数组
      inputMessage: '', // 输入框中的消息内容
      isLoading: false, // 发送按钮的加载状态
      chatHistories: [], // 所有聊天历史记录
      favoriteHistories: [], // 收藏的聊天历史记录
      currentHistoryId: null, // 当前选中的历史记录ID
      historyCollapsed: false, // 历史记录侧边栏是否折叠
      activeHistoryTab: 'all', // 当前选中的历史记录选项卡
      renameDialogVisible: false, // 重命名对话框是否可见
      newHistoryTitle: '', // 新的历史记录标题
      historyToRename: null // 要重命名的历史记录ID
    };
  },
  mounted() {
    // 在组件挂载后加载聊天历史记录
    this.loadChatHistories();
  },
  methods: {
    // 格式化日期方法
    formatDate(dateString) {
      const date = new Date(dateString);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      // 如果是今天
      if (date.toDateString() === today.toDateString()) {
        return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      }
      // 如果是昨天
      else if (date.toDateString() === yesterday.toDateString()) {
        return `昨天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      }
      // 其他日期
      else {
        return `${date.getMonth() + 1}月${date.getDate()}日`;
      }
    },
    
    // 加载聊天历史记录
    async loadChatHistories() {
      try {
        // 获取所有聊天历史记录
        const response = await axios.get('/chat/histories');
        this.chatHistories = response.data.histories;
        
        // 加载收藏的聊天历史记录
        const favResponse = await axios.get('/chat/favorites');
        this.favoriteHistories = favResponse.data.favorites;
        
        // 如果存在历史记录且当前没有选中的历史记录，则选中最新的一条
        if (this.chatHistories.length > 0 && !this.currentHistoryId) {
          // 按更新时间排序，选择最新的一条
          const sortedHistories = [...this.chatHistories].sort((a, b) => 
            new Date(b.updated_at) - new Date(a.updated_at)
          );
          this.switchHistory(sortedHistories[0].id);
        }
      } catch (error) {
        console.error('加载聊天历史记录失败:', error);
        this.$message.error('加载聊天历史记录失败');
      }
    },
    
    // 创建新的聊天
    async createNewChat() {
      try {
        const response = await axios.post('/chat/histories', {
          title: `对话 ${new Date().toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' })}`
        });
        
        if (response.data.status === 'success') {
          // 创建成功后重新加载历史记录
          await this.loadChatHistories();
          // 切换到新创建的聊天
          this.switchHistory(response.data.history_id);
        }
      } catch (error) {
        console.error('创建新聊天失败:', error);
        this.$message.error('创建新聊天失败');
      }
    },
    
    // 切换聊天历史记录
    async switchHistory(historyId) {
      try {
        const response = await axios.get(`/chat/histories/${historyId}`);
        if (response.data.status === 'success') {
          this.currentHistoryId = historyId;
          this.messages = response.data.history.messages;
          
          // 滚动到消息列表底部
          this.$nextTick(() => {
            if (this.$refs.messageList) {
              this.$refs.messageList.scrollTop = this.$refs.messageList.scrollHeight;
            }
          });
        }
      } catch (error) {
        console.error('切换聊天历史记录失败:', error);
        this.$message.error('切换聊天历史记录失败');
      }
    },
    
    // 切换收藏状态
    async toggleFavorite(historyId) {
      try {
        const response = await axios.put(`/chat/histories/${historyId}/favorite`);
        if (response.data.status === 'success') {
          // 切换成功后重新加载历史记录
          await this.loadChatHistories();
        }
      } catch (error) {
        console.error('切换收藏状态失败:', error);
        this.$message.error('切换收藏状态失败');
      }
    },
    
    // 处理历史记录操作
    handleHistoryAction(command, historyId) {
      if (command === 'rename') {
        // 打开重命名对话框
        const history = this.chatHistories.find(h => h.id === historyId);
        if (history) {
          this.newHistoryTitle = history.title;
          this.historyToRename = historyId;
          this.renameDialogVisible = true;
        }
      } else if (command === 'delete') {
        // 确认删除
        this.$confirm('确定要删除这个对话吗？此操作不可恢复。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.deleteHistory(historyId);
        }).catch(() => {
          // 取消删除操作
        });
      }
    },
    
    // 确认重命名
    async confirmRename() {
      if (!this.newHistoryTitle.trim()) {
        this.$message.warning('对话名称不能为空');
        return;
      }
      
      try {
        const response = await axios.put(`/chat/histories/${this.historyToRename}/title`, {
          title: this.newHistoryTitle
        });
        
        if (response.data.status === 'success') {
          // 重命名成功后重新加载历史记录
          await this.loadChatHistories();
          this.renameDialogVisible = false;
          this.$message.success('重命名成功');
        }
      } catch (error) {
        console.error('重命名失败:', error);
        this.$message.error('重命名失败');
      }
    },
    
    // 删除历史记录
    async deleteHistory(historyId) {
      try {
        const response = await axios.delete(`/chat/histories/${historyId}`);
        if (response.data.status === 'success') {
          // 删除成功后重新加载历史记录
          await this.loadChatHistories();
          
          // 如果删除的是当前选中的历史记录，则选中另一条
          if (this.currentHistoryId === historyId) {
            if (this.chatHistories.length > 0) {
              this.switchHistory(this.chatHistories[0].id);
            } else {
              // 如果没有历史记录了，则创建一个新的
              this.createNewChat();
            }
          }
          
          this.$message.success('删除成功');
        }
      } catch (error) {
        console.error('删除失败:', error);
        this.$message.error('删除失败');
      }
    },
    
    // 发送消息方法
    async sendMessage() {
      if (!this.inputMessage.trim()) return; // 如果输入为空，则不发送
      
      // 如果没有当前历史记录ID，则创建一个新的
      if (!this.currentHistoryId) {
        await this.createNewChat();
      }
      
      this.isLoading = true; // 设置加载状态为 true
      const userMessage = { role: 'user', content: this.inputMessage }; // 创建用户消息对象
      this.messages.push(userMessage); // 将用户消息添加到消息列表
      
      // 滚动到消息列表底部
      this.$nextTick(() => {
        if (this.$refs.messageList) {
          this.$refs.messageList.scrollTop = this.$refs.messageList.scrollHeight;
        }
      });
      
      try {
        // 发送 POST 请求到后端 API
        const response = await axios.post('/v1/chat/completions', {
          messages: this.messages, // 发送当前所有消息
          model: 'default', // 使用默认模型
          history_id: this.currentHistoryId // 传递历史记录ID
        });
        
        // 将 AI 助手的回复添加到消息列表
        this.messages.push({
          role: 'assistant',
          content: response.data.choices[0].message.content
        });
        
        // 滚动到消息列表底部
        this.$nextTick(() => {
          if (this.$refs.messageList) {
            this.$refs.messageList.scrollTop = this.$refs.messageList.scrollHeight;
          }
        });
        
        // 重新加载历史记录以更新最新状态
        await this.loadChatHistories();
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
/* 聊天主容器样式 */
.chat-main-container {
  display: flex;
  height: calc(100vh - 120px);
  background: #f8f9fa;
}

/* 历史记录侧边栏样式 */
.history-sidebar {
  width: 280px;
  border-right: 1px solid #e6e6e6;
  background: white;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 侧边栏折叠状态 */
.history-sidebar.collapsed {
  width: 0;
}

/* 侧边栏头部样式 */
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

/* 历史记录选项卡样式 */
.history-tabs {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.history-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

/* 历史记录列表样式 */
.history-list {
  padding: 8px;
  overflow-y: auto;
}

/* 历史记录项样式 */
.history-item {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item:hover {
  background: #f5f7fa;
}

.history-item.active {
  background: #ecf5ff;
}

/* 历史记录标题包装器样式 */
.history-title-wrapper {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* 历史记录标题样式 */
.history-title {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 历史记录日期样式 */
.history-date {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 历史记录操作按钮样式 */
.history-actions {
  display: flex;
  align-items: center;
  visibility: hidden;
}

.history-item:hover .history-actions {
  visibility: visible;
}

/* 折叠按钮样式 */
.collapse-button {
  padding: 4px;
  margin-left: 8px;
}

/* 聊天容器样式 */
.chat-container {
  display: flex; /* 弹性布局 */
  flex-direction: column; /* 垂直方向排列 */
  flex: 1;
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

/* 消息头像样式 */
.message-avatar {
  margin: 0 12px;
}

/* 消息内容包装器样式 */
.message-content-wrapper {
  background: white;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

/* 用户消息内容包装器样式 */
.message-bubble.user .message-content-wrapper {
  background: #409EFF;
  color: white;
}

/* 消息角色样式 */
.message-role {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #606266;
}

/* 用户消息角色样式 */
.message-bubble.user .message-role {
  color: rgba(255, 255, 255, 0.9);
}

/* 消息内容样式 */
.message-content {
  word-break: break-word;
  line-height: 1.5;
}

/* 输入区域样式 */
.input-area {
  padding: 20px; /* 内边距 */
  border-top: 1px solid #e6e6e6; /* 上边框 */
  background: white;
  display: flex;
  flex-direction: column;
}

/* 发送按钮样式 */
.send-button {
  margin-top: 12px;
  align-self: flex-end;
}

/* 对话框底部样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>