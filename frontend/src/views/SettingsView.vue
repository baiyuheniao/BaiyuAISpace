<template>
  <div class="settings-container">
    <div class="settings-header">
      <h2 class="settings-title">服务商配置</h2>
      <p class="settings-description">选择并配置您的AI服务提供商</p>
    </div>
    
    <el-card class="settings-card">
      <el-form label-position="top">
        <el-form-item label="MCP模式">
          <el-switch v-model="enableMCP" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        
        <el-form-item label="当前提供商">
          <el-select 
            v-model="currentProvider" 
            placeholder="请选择提供商"
            class="provider-select"
            filterable
            @change="handleProviderChange" 
          >
            <el-option
              v-for="provider in providers"
              :key="provider.name"
              :label="provider.name"
              :value="provider.name"
            />
          </el-select>
        </el-form-item>
        
        <div v-if="currentProvider">
          <el-form-item label="API 密钥" required>
            <el-input 
              v-model="apiKey" 
              placeholder="请输入您的 API 密钥" 
              type="password"
              show-password
              class="api-input"
            />
          </el-form-item>

          <el-form-item label="模型名称" required>
            <el-input 
              v-model="modelName" 
              placeholder="请输入调用的模型名称"
              class="api-input"
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="Temperature (0-2)">
                <el-input-number 
                  v-model="temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  controls-position="right"
                  placeholder="例如 0.7"
                  class="param-input"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Top K">
                <el-input-number 
                  v-model="topK"
                  :min="1"
                  controls-position="right"
                  placeholder="例如 40"
                  class="param-input"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Max Tokens">
                <el-input-number 
                  v-model="maxTokens"
                  :min="1"
                  controls-position="right"
                  placeholder="例如 1024"
                  class="param-input"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-button 
            type="primary" 
            @click="saveSettings"
            :loading="isSaving"
            class="save-button"
          >
            <el-icon><Check /></el-icon>
            <span>保存设置</span>
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SettingsView',
  data() {
    return {
      enableMCP: false,
      providers: [
        { name: 'OpenAI' },
        { name: 'Anthropic' },
        { name: 'Meta' },
        { name: 'Google' },
        { name: 'Cohere' },
        { name: 'Replicate' },
        { name: '阿里云' },
        { name: '智谱' },
        { name: 'Mistral' },
        { name: 'DeepSeek' },
        { name: 'Lambda Labs' },
        { name: '硅基流动' },
        { name: '其他' }
      ],
      currentProvider: '',
      apiKey: '',
      modelName: '',
      temperature: 0.7,
      topK: null,
      maxTokens: 1024,
      isSaving: false
    };
  },
  methods: {
    handleProviderChange() {
      // 切换提供商时可以重置或加载特定配置，暂时留空
      this.apiKey = '';
      this.modelName = '';
      // 可以根据选择的提供商设置默认模型等
    },
    async saveSettings() {
      // 1. 验证输入
      if (!this.currentProvider) {
        this.$message.error('请先选择一个服务提供商');
        return;
      }
      if (!this.apiKey.trim()) {
        this.$message.error('请输入 API 密钥');
        return;
      }
      if (!this.modelName.trim()) {
        this.$message.error('请输入模型名称');
        return;
      }

      // 准备要发送的配置数据
      const config = {
        api_key: this.apiKey,
        model: this.modelName,
        // 只包含用户实际修改过的参数，或有值的参数
        ...(this.temperature !== null && { temperature: this.temperature }),
        ...(this.topK !== null && { top_k: this.topK }),
        ...(this.maxTokens !== null && { max_tokens: this.maxTokens }),
      };

      this.isSaving = true;
      try {
        // 2. 发送请求到后端
        if (this.enableMCP) {
          await axios.post('/mcp/save_config', {
            provider_name: this.currentProvider,
            config: config
          });
        }
        await axios.post('/switch_provider', {
          provider_name: this.currentProvider,
          config: config // 发送结构化的配置
        });
        // 3. 成功提示并跳转
        this.$message.success('设置保存成功，即将跳转到对话页面...');
        // 延迟跳转，给用户看提示的时间
        setTimeout(() => {
          this.$router.push('/chat');
        }, 1500);
      } catch (error) {
        // 4. 错误处理
        console.error('保存失败:', error);
        const errorMsg = error.response?.data?.error || '保存设置失败，请检查配置或稍后再试';
        this.$message.error(errorMsg);
      } finally {
        this.isSaving = false;
      }
    }
  },
  async created() {
    // 这里可以添加获取当前配置的逻辑，并填充表单
    // 例如：
    // try {
    //   const response = await axios.get('/current_config');
    //   const { provider_name, config } = response.data;
    //   this.currentProvider = provider_name;
    //   this.apiKey = config.api_key || '';
    //   this.modelName = config.model || '';
    //   this.temperature = config.temperature ?? 0.7;
    //   this.topK = config.top_k ?? null;
    //   this.maxTokens = config.max_tokens ?? 1024;
    // } catch (error) {
    //   console.error('获取当前配置失败:', error);
    //   // 可以选择性地提示用户
    // }
  }
};
</script>

<style scoped>
.settings-container {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 24px;
}

.settings-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.settings-description {
  color: var(--el-text-color-secondary);
  margin: 0;
}

.settings-card {
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.provider-select {
  width: 100%;
}

.api-input,
.param-input .el-input__inner { /* 确保数字输入框内部也应用字体 */
  font-family: 'Fira Code', monospace;
}

.param-input {
    width: 100%; /* 让数字输入框占满列宽 */
}

.save-button {
  width: 100%;
  margin-top: 16px;
}

.el-form-item {
  margin-bottom: 24px;
}

/* 调整数字输入框的样式 */
.el-input-number {
  width: 100%;
}
</style>