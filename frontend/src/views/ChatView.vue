<template>
  <!-- 聊天主容器 -->
  <div class="chat-main-container">
    <!-- 历史记录侧边栏 -->
    <transition name="history-slide">
      <div
        class="history-sidebar"
        :class="{ 'collapsed': historyCollapsed, 'auto-expanded': historyAutoExpand }"
        :style="{ left: historySidebarLeft }"
        @mouseenter="expandHistory"
        @mouseleave="collapseHistory"
      >
        <div class="sidebar-header">
          <h3>聊天历史</h3>
          <el-button type="primary" size="small" @click="createNewChat">
            <el-icon><Plus /></el-icon>
            新对话
          </el-button>
          <el-button type="text" class="collapse-button" @click="toggleHistorySidebar">
            <el-icon><ArrowLeft v-if="!historyCollapsed" /><ArrowRight v-else /></el-icon>
          </el-button>
        </div>
        
        <!-- 历史记录选项卡 -->
        <el-tabs v-if="!historyCollapsed || historyAutoExpand" v-model="activeHistoryTab" class="history-tabs">
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
    </transition>
    
    <div class="chat-content" :style="{ marginLeft: chatContentMargin }">
      <!-- 历史记录浮动按钮 - 当侧边栏折叠时显示 -->
      <div 
        v-if="historyCollapsed && !historyAutoExpand" 
        class="history-float-button" 
        :style="{ left: historyFloatButtonLeft }"
        @click="expandHistorySidebar"
      >
        <el-button type="primary" circle>
          <el-icon><ChatDotRound /></el-icon>
        </el-button>
        <span class="float-button-tooltip">聊天历史</span>
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
          <!-- 配置切换区域 -->
          <div class="config-switcher" v-if="savedConfigs && Object.keys(savedConfigs).length > 0">
            <div class="config-switcher-header">
              <span class="config-label">当前配置:</span>
              <el-dropdown @command="switchConfig" trigger="click">
                <el-button type="text" class="config-dropdown">
                  <span class="current-config-name">{{ currentConfigName }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item 
                      v-for="(config, providerName) in savedConfigs" 
                      :key="providerName"
                      :command="providerName"
                      :class="{ 'current-config': providerName === currentProviderName }"
                    >
                      <div class="config-option">
                        <span class="provider-name">{{ providerName }}</span>
                        <span class="model-name">{{ config.model || '未设置模型' }}</span>
                        <el-tag v-if="providerName === currentProviderName" type="success" size="small">当前</el-tag>
                      </div>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button type="text" size="small" @click="goToSettings">
                <el-icon><Setting /></el-icon>
                管理配置
              </el-button>
            </div>
          </div>
          
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
  </div>
</template>

<script>
import axios from 'axios'; // 导入 axios 用于 HTTP 请求
import { Plus, ArrowLeft, ArrowRight, Star, More, ArrowDown, Setting, ChatDotRound } from '@element-plus/icons-vue'; // 导入图标

export default {
  name: 'ChatView', // 组件名称
  components: {
    Plus,
    ArrowLeft,
    ArrowRight,
    Star,
    More,
    ArrowDown,
    Setting,
    ChatDotRound
  },
  data() { // 组件数据
    return {
      messages: [], // 存储聊天消息的数组
      inputMessage: '', // 输入框中的消息内容
      isLoading: false, // 发送按钮的加载状态
      chatHistories: [], // 所有聊天历史记录
      favoriteHistories: [], // 收藏的聊天历史记录
      currentHistoryId: null, // 当前选中的历史记录ID
      historyCollapsed: false,
      historyAutoExpand: false, // 新增自动展开标志
      activeHistoryTab: 'all', // 当前选中的历史记录选项卡
      renameDialogVisible: false, // 重命名对话框是否可见
      newHistoryTitle: '', // 新的历史记录标题
      historyToRename: null, // 要重命名的历史记录ID
      sidebarExpanded: false, // 新增，响应SidebarNav展开状态
      savedConfigs: {}, // 存储配置
      currentConfigName: '', // 当前配置名称
      currentProviderName: '', // 当前配置提供者
    };
  },
  mounted() {
    // 在组件挂载后加载聊天历史记录
    // this.loadChatHistories(); // 暂时注释掉，因为后端功能未实现
    console.log('聊天页面已加载，聊天历史功能暂未实现');
    // 监听SidebarNav展开状态
    window.addEventListener('sidebar-nav-toggle', this.handleSidebarToggle)
    
    // 加载已保存的配置
    this.loadSavedConfigs();
  },
  beforeUnmount() {
    window.removeEventListener('sidebar-nav-toggle', this.handleSidebarToggle)
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
        console.log('聊天历史功能暂未实现');
        // 不显示错误提示，因为这是预期的情况
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
        console.log('聊天历史功能暂未实现');
        this.$message.info('聊天历史功能暂未实现，但可以正常发送消息');
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
        console.log('聊天历史功能暂未实现');
        // 不显示错误提示，因为这是预期的情况
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
        console.log('聊天历史功能暂未实现');
        this.$message.info('收藏功能暂未实现');
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
        console.log('聊天历史功能暂未实现');
        this.$message.info('重命名功能暂未实现');
        this.renameDialogVisible = false;
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
        console.log('聊天历史功能暂未实现');
        this.$message.info('删除功能暂未实现');
      }
    },
    
    // 发送消息方法
    async sendMessage() {
      if (!this.inputMessage.trim()) return; // 如果输入为空，则不发送
      
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
          model: 'default' // 使用默认模型
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
      } catch (error) {
        console.error('请求失败:', error); // 打印错误信息
        let errorMsg = '发送消息失败';
        
        // 尝试从不同位置获取错误信息
        if (error.response?.data?.detail) {
          errorMsg = error.response.data.detail;
        } else if (error.response?.data?.error) {
          errorMsg = error.response.data.error;
        } else if (error.message) {
          errorMsg = error.message;
        }
        
        this.$message.error(errorMsg); // 显示错误提示
      } finally {
        this.isLoading = false; // 无论成功或失败，都将加载状态设置为 false
        this.inputMessage = ''; // 清空输入框
      }
    },
    toggleHistorySidebar() {
      // 修复缩回报错：只切换collapsed，不影响autoExpand
      this.historyCollapsed = !this.historyCollapsed
      this.historyAutoExpand = false
    },
    expandHistory() {
      if (this.historyCollapsed) {
        this.historyAutoExpand = true
      }
    },
    collapseHistory() {
      if (this.historyCollapsed) {
        this.historyAutoExpand = false
      }
    },
    expandHistorySidebar() {
      // 展开历史侧边栏
      this.historyCollapsed = false
      this.historyAutoExpand = false
    },
    handleSidebarToggle(e) {
      this.sidebarExpanded = !!e.detail
    },
    async switchConfig(providerName) {
      try {
        // 调用后端API切换配置
        await axios.post('/switch_provider', {
          provider_name: providerName,
          config: this.savedConfigs[providerName]
        });
        
        this.currentProviderName = providerName;
        this.currentConfigName = providerName;
        this.$message.success(`已切换到 ${providerName} 配置`);
      } catch (error) {
        console.error('切换配置失败:', error);
        let errorMsg = '切换配置失败';
        if (error.response?.data?.detail) {
          errorMsg = error.response.data.detail;
        }
        this.$message.error(errorMsg);
      }
    },
    goToSettings() {
      // 实现跳转到配置管理页面的逻辑
      console.log('跳转到配置管理页面');
      this.$router.push('/settings');
    },
    // 加载已保存的配置
    async loadSavedConfigs() {
      try {
        const response = await axios.get('/chat/configs');
        if (response.data.status === 'success') {
          this.savedConfigs = response.data.configs || {};
          this.currentProviderName = response.data.current_provider || '';
          
          // 设置当前配置名称
          if (this.currentProviderName && this.savedConfigs[this.currentProviderName]) {
            this.currentConfigName = this.currentProviderName;
          } else if (Object.keys(this.savedConfigs).length > 0) {
            // 如果没有当前配置，使用第一个配置
            this.currentConfigName = Object.keys(this.savedConfigs)[0];
            this.currentProviderName = this.currentConfigName;
          }
        }
      } catch (error) {
        console.log('加载配置失败:', error);
        this.$message.info('加载配置失败');
      }
    },
  },
  computed: {
    chatContentMargin() {
      // 基础边距（为导航栏预留）
      const baseMargin = this.sidebarExpanded ? 160 : 56;
      
      // 如果历史侧边栏展开或自动展开，添加侧边栏宽度
      if (!this.historyCollapsed || this.historyAutoExpand) {
        // 如果是折叠状态但自动展开，使用较小的宽度
        const sidebarWidth = this.historyCollapsed && this.historyAutoExpand ? 220 : 280;
        return `${baseMargin + sidebarWidth}px`;
      }
      
      // 如果历史侧边栏完全折叠，只返回基础边距
      return `${baseMargin}px`;
    },
    historySidebarLeft() {
      // 根据主导航栏的展开状态调整历史侧边栏的位置
      return this.sidebarExpanded ? '160px' : '56px';
    },
    historyFloatButtonLeft() {
      // 根据主导航栏的展开状态调整浮动按钮的位置
      return this.sidebarExpanded ? '184px' : '80px';
    }
  }
};
</script>

<style scoped>
/* 聊天主容器样式 */
.chat-main-container {
  display: flex;
  height: 100vh;
  background: #f8f9fa;
  position: relative;
  overflow: hidden;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  transition: margin-left 0.3s cubic-bezier(.4,0,.2,1);
  will-change: margin-left;
}

/* 历史记录侧边栏样式 */
.history-sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 280px;
  border-right: 1px solid #e6e6e6;
  background: white;
  transition: width 0.3s cubic-bezier(.4,0,.2,1), left 0.3s cubic-bezier(.4,0,.2,1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 999; /* 低于主导航栏 */
  box-shadow: 2px 0 8px 0 rgba(0,0,0,0.1);
  will-change: width, left;
}

.history-sidebar.collapsed:not(.auto-expanded) {
  width: 0;
  min-width: 0;
  overflow: hidden;
}

.history-sidebar.auto-expanded {
  width: 220px;
  min-width: 180px;
  box-shadow: 2px 0 8px 0 rgba(0,0,0,0.04);
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
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 20px;
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

/* 配置切换区域样式 */
.config-switcher {
  margin-bottom: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.config-switcher-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.config-label {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
}

.config-dropdown {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  color: #606266;
  transition: all 0.3s ease;
}

.config-dropdown:hover {
  border-color: #409eff;
  color: #409eff;
}

.current-config-name {
  margin-right: 8px;
  font-weight: 500;
}

.config-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}

.provider-name {
  margin-right: 8px;
  font-weight: 500;
}

.model-name {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
}

.current-config {
  background-color: #e6f7ff;
}

.current-config .provider-name {
  color: #409eff;
  font-weight: 600;
}

/* 历史记录浮动按钮样式 */
.history-float-button {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 998;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.history-float-button:hover {
  transform: translateY(-50%) scale(1.1);
}

.float-button-tooltip {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.history-float-button:hover .float-button-tooltip {
  opacity: 1;
}


</style>