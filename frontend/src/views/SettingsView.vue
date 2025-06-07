<template>
  <!-- 设置页面容器 -->
  <div class="settings-container">
    <!-- 设置头部区域 -->
    <div class="settings-header">
      <h2 class="settings-title">服务商配置</h2>
      <p class="settings-description">选择并配置您的AI服务提供商</p>
    </div>
    
    <!-- 设置卡片区域 -->
    <el-card class="settings-card">
      <!-- 表单，标签位置在上方 -->
      <el-form label-position="top">
          <!-- API 提供商选择项 -->
          <el-form-item label="API提供商">
            <el-select v-model="currentProvider" placeholder="请选择API提供商" @change="handleProviderChange">
              <el-option v-for="provider in providers" :key="provider.name" :label="provider.name" :value="provider.name"></el-option>
            </el-select>
          </el-form-item>

          <!-- 当选择了提供商后显示配置项 -->
          <div v-if="currentProvider">
            <!-- API 密钥输入项 -->
            <el-form-item label="API 密钥" required>
              <el-input 
                v-model="apiKey" 
                placeholder="请输入您的 API 密钥" 
                type="password" <!-- 密码类型输入框 -->
                show-password <!-- 显示密码切换按钮 -->
                class="api-input"
              />
            </el-form-item>

            <!-- 模型名称输入项 -->
            <el-form-item label="模型名称" required>
              <el-input 
                v-model="modelName" 
                placeholder="请输入调用的模型名称"
                class="api-input"
              />
            </el-form-item>

            <!-- 参数设置行 -->
            <el-row :gutter="20">
              <!-- Temperature 参数设置 -->
              <el-col :span="6">
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
              <!-- Max Tokens 参数设置 -->
              <el-col :span="6">
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
              <!-- Top K 参数设置 -->
              <el-col :span="6">
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
              <!-- Top P 参数设置 -->
              <el-col :span="6">
                <el-form-item label="Top P (0-1)">
                  <el-input-number 
                    v-model="topP"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    controls-position="right"
                    placeholder="例如 0.9"
                    class="param-input"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- MCP 模式开关 -->
          <el-form-item label="MCP模式">
            <el-switch v-model="enableMCP" @change="handleMcpModeChange"></el-switch>
          </el-form-item>

          <!-- MCP 配置输入框，当 MCP 模式开启时显示 -->
          <el-form-item label="MCP配置" v-if="enableMCP">
            <el-input
              type="textarea"
              :rows="10"
              v-model="mcpConfig"
              placeholder='例如: { &quot;provider_name&quot;: { &quot;api_key&quot;: &quot;your_api_key&quot;, &quot;model_name&quot;: &quot;your_model_name&quot; } }'
            ></el-input>
          </el-form-item>

          <!-- 保存设置按钮 -->
          <el-button 
            type="primary" 
            @click="saveSettings"
            :loading="isSaving"
            class="save-button"
          >
            <el-icon><Check /></el-icon>
            <span>保存设置</span>
          </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'; // 导入 axios 用于 HTTP 请求
import { Check, Download, Upload } from '@element-plus/icons-vue'; // 导入 Element Plus 图标

export default {
  name: 'SettingsView', // 组件名称
  components: { // 注册组件
    Check,
    Download,
    Upload
  },
  data() { // 组件数据
    return {
      enableMCP: false, // 是否启用 MCP 模式
      mcpConfig: '', // MCP 配置的 JSON 字符串
      providers: [ // 可用的 API 提供商列表
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
      currentProvider: '', // 当前选择的提供商
      apiKey: '', // API 密钥
      modelName: '', // 模型名称
      temperature: 1, // 温度参数
      topK: null, // Top K 参数
      maxTokens: null, // 最大 token 数
      topP: null, // Top P 参数
      isSaving: false, // 保存按钮加载状态
      isExporting: false, // 导出按钮加载状态
      isImporting: false // 导入按钮加载状态
    };
  },
  methods: { // 组件方法
    handleProviderChange() { // 处理提供商选择变化
      // 切换提供商时可以重置或加载特定配置，暂时留空
      this.apiKey = '';
      this.modelName = '';
      // 可以根据选择的提供商设置默认模型等
    },
    async saveSettings() { // 保存设置方法
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
        ...(this.topP !== null && { top_p: this.topP }),
      };

      this.isSaving = true; // 设置保存按钮加载状态为 true
      try {
        // 2. 发送请求到后端
        if (this.enableMCP) { // 如果启用了 MCP 模式
          try {
            JSON.parse(this.mcpConfig); // 验证 MCP 配置的 JSON 格式
            await axios.post('/mcp/save_config', { // 发送保存 MCP 配置的请求
              provider_name: this.currentProvider,
              config: config,
              mcp_config: JSON.parse(this.mcpConfig)
            });
          } catch (e) {
            this.$message.error('MCP配置JSON格式错误: ' + e.message); // 提示 JSON 格式错误
            throw e; // 抛出异常
          }
        }
        // 发送切换提供商的请求
        await axios.post('/switch_provider', {
          provider_name: this.currentProvider,
          config: config // 发送结构化的配置
        });
        // 3. 成功提示并跳转
        this.$message.success('设置保存成功，即将跳转到对话页面...'); // 显示成功提示
        // 延迟跳转，给用户看提示的时间
        setTimeout(() => {
          this.$router.push('/chat'); // 跳转到聊天页面
        }, 1500);
      } catch (error) {
        // 4. 错误处理
        console.error('保存失败:', error); // 打印错误信息
        const errorMsg = error.response?.data?.error || '保存设置失败，请检查配置或稍后再试'; // 获取错误信息
        this.$message.error(errorMsg); // 显示错误提示
      } finally {
        this.isSaving = false; // 无论成功或失败，都将保存按钮加载状态设置为 false
      }
    },
    async exportConfig() { // 导出配置方法
      this.isExporting = true; // 设置导出按钮加载状态为 true
      try {
        const response = await axios.get('/mcp/export_config'); // 发送导出配置的请求
        const configData = response.data; // 获取配置数据
        const blob = new Blob([JSON.stringify(configData, null, 2)], { type: 'application/json' }); // 创建 Blob 对象
        const url = URL.createObjectURL(blob); // 创建 URL
        const a = document.createElement('a'); // 创建 a 标签
        a.href = url;
        a.download = 'mcp_config.json'; // 设置下载文件名
        document.body.appendChild(a); // 将 a 标签添加到 body
        a.click(); // 模拟点击
        document.body.removeChild(a); // 移除 a 标签
        URL.revokeObjectURL(url); // 释放 URL
        this.$message.success('配置导出成功！'); // 显示成功提示
      } catch (error) {
        console.error('导出配置失败:', error); // 打印错误信息
        this.$message.error('导出配置失败，请稍后再试。'); // 显示错误提示
      } finally {
        this.isExporting = false; // 无论成功或失败，都将导出按钮加载状态设置为 false
      }
    },
    handleImportSuccess(response, file, fileList) { // 处理导入成功
      this.$message.success('配置导入成功！'); // 显示成功提示
      // 导入成功后，可以考虑重新加载配置或刷新页面
      // 例如：this.loadCurrentConfig();
    },
    handleImportError(error, file, fileList) { // 处理导入失败
      console.error('导入配置失败:', error); // 打印错误信息
      this.$message.error('导入配置失败，请检查文件格式或稍后再试。'); // 显示错误提示
    },
    beforeImportUpload(file) { // 导入前检查文件类型
      const isJson = file.type === 'application/json'; // 检查是否是 JSON 文件
      if (!isJson) {
        this.$message.error('只能上传 JSON 格式的文件!'); // 提示文件格式错误
      }
      return isJson;
    },
    handleImportFile(file) { // 处理导入文件
      const reader = new FileReader(); // 创建 FileReader 对象
      reader.onload = async (e) => { // 文件读取完成回调
        try {
          const config = JSON.parse(e.target.result); // 解析 JSON 内容
          this.isImporting = true; // 设置导入按钮加载状态为 true
          await axios.post('/mcp/import_config', config); // 发送导入配置的请求
          this.$message.success('配置导入成功！'); // 显示成功提示
          // 导入成功后，重新加载配置以更新 UI
          // this.loadCurrentConfig(); // 如果有加载当前配置的方法，可以在这里调用
        } catch (error) {
          console.error('导入配置失败:', error); // 打印错误信息
          this.$message.error('导入配置失败，请检查文件内容或稍后再试。'); // 显示错误提示
        } finally {
          this.isImporting = false; // 无论成功或失败，都将导入按钮加载状态设置为 false
        }
      };
      reader.readAsText(file.raw); // 读取文件内容为文本
    }
  },
  async created() { // 组件创建后生命周期钩子
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
/* 设置容器样式 */
.settings-container {
  padding: 24px; /* 内边距 */
  max-width: 800px; /* 最大宽度 */
  margin: 0 auto; /* 水平居中 */
}

/* 设置头部样式 */
.settings-header {
  margin-bottom: 24px; /* 下外边距 */
}

/* 设置标题样式 */
.settings-title {
  font-size: 1.5rem; /* 字体大小 */
  font-weight: 600; /* 字体粗细 */
  margin-bottom: 8px; /* 下外边距 */
  color: var(--el-text-color-primary); /* 文本颜色 */
}

/* 设置描述样式 */
.settings-description {
  color: var(--el-text-color-secondary); /* 文本颜色 */
  margin: 0; /* 外边距 */
}

/* 设置卡片样式 */
.settings-card {
  padding: 24px; /* 内边距 */
  border-radius: 12px; /* 圆角 */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); /* 阴影效果 */
}

/* 提供商选择器样式 */
.provider-select {
  width: 100%; /* 宽度占满 */
}

/* API 输入框和参数输入框内部字体样式 */
.api-input,
.param-input .el-input__inner { /* 确保数字输入框内部也应用字体 */
  font-family: 'Fira Code', monospace; /* 字体 */
}

/* 参数输入框样式 */
.param-input {
    width: 100%; /* 让数字输入框占满列宽 */
}

/* MCP 配置操作按钮区域样式 */
.mcp-config-actions {
  margin-top: 10px; /* 上外边距 */
  display: flex; /* 弹性布局 */
  gap: 10px; /* 间距 */
}

/* 保存按钮样式 */
.save-button {
  margin-top: 20px; /* 上外边距 */
  width: 100%; /* 宽度占满 */
}

/* 表单项样式 */
.el-form-item {
  margin-bottom: 24px; /* 下外边距 */
}

/* 调整数字输入框的样式 */
.el-input-number {
  width: 100%; /* 宽度占满 */
}
</style>