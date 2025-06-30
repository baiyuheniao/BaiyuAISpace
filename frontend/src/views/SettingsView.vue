<template>
  <div class="settings-main-container">
    <div class="settings-content">
      <!-- 设置页面容器 -->
      <div class="settings-container">
        <!-- 设置头部区域 -->
        <div class="settings-header">
          <h2 class="settings-title">服务商配置</h2>
          <p class="settings-description">选择并配置您的AI服务提供商</p>
        </div>
        
        <!-- 已保存配置列表 -->
        <el-card class="saved-configs-card" v-if="Object.keys(savedConfigs).length > 0">
          <template #header>
            <div class="card-header">
              <span>已保存的配置</span>
              <el-button type="primary" size="small" @click="loadSavedConfigs">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="saved-configs-list">
            <div 
              v-for="(config, providerName) in savedConfigs" 
              :key="providerName" 
              class="saved-config-item"
              :class="{ 'current': providerName === currentProviderName }"
            >
              <div class="config-info">
                <div class="provider-name">
                  {{ providerName }}
                  <el-tag v-if="providerName === currentProviderName" type="success" size="small">当前</el-tag>
                </div>
                <div class="config-details">
                  <span class="model-name">模型: {{ config.model || '未设置' }}</span>
                  <span class="api-key">API密钥: {{ maskApiKey(config.api_key) }}</span>
                </div>
              </div>
              <div class="config-actions">
                <el-button type="primary" size="small" @click="loadConfig(providerName, config)">
                  加载
                </el-button>
                <el-button type="danger" size="small" @click="deleteConfig(providerName)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 设置卡片区域 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>配置新服务商</span>
              <el-button v-if="currentProvider" type="info" size="small" @click="clearForm">
                清空表单
              </el-button>
            </div>
          </template>
          
          <!-- 配置文件路径设置 -->
          <div class="config-path-section">
            <h3 class="section-title">配置文件存储设置</h3>
            <el-form label-position="top">
              <el-form-item label="配置文件路径">
                <div class="config-path-input">
                  <el-input 
                    v-model="configPath" 
                    placeholder="请输入配置文件存储路径，例如: ./config/mcp_config.json"
                    class="path-input"
                  />
                  <el-button type="primary" @click="setConfigPath" :loading="isSettingPath">
                    设置路径
                  </el-button>
                </div>
                <div class="path-info">
                  <span class="current-path">当前路径: {{ currentConfigPath }}</span>
                  <el-button type="text" size="small" @click="loadConfigPath">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
            
            <!-- 备份和恢复功能 -->
            <div class="backup-restore-section">
              <h4 class="subsection-title">配置备份与恢复</h4>
              <div class="backup-actions">
                <el-button type="success" @click="backupConfig" :loading="isBackingUp">
                  <el-icon><Download /></el-icon>
                  备份配置
                </el-button>
                <el-upload
                  ref="restoreUpload"
                  :show-file-list="false"
                  :before-upload="beforeRestoreUpload"
                  :on-success="handleRestoreSuccess"
                  :on-error="handleRestoreError"
                  accept=".json"
                  action="#"
                  :http-request="handleRestoreFile"
                >
                  <el-button type="warning" :loading="isRestoring">
                    <el-icon><Upload /></el-icon>
                    恢复配置
                  </el-button>
                </el-upload>
                <el-button type="info" @click="showDebugInfo">
                  <el-icon><InfoFilled /></el-icon>
                  调试信息
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 分隔线 -->
          <el-divider content-position="left">服务商配置</el-divider>
          
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
                    type="password"
                    show-password
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

                <!-- Base URL 输入项，仅对自定义提供商显示 -->
                <el-form-item label="API Base URL" v-if="isCustomProvider">
                  <el-input 
                    v-model="baseUrl" 
                    placeholder="请输入API基础URL，例如: https://api.example.com"
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
    </div>
  </div>
</template>

<script>
import axios from 'axios'; // 导入 axios 用于 HTTP 请求
import { Check, Download, Upload, Refresh, InfoFilled } from '@element-plus/icons-vue'; // 导入 Element Plus 图标

export default {
  name: 'SettingsView', // 组件名称
  components: { // 注册组件
    Check,
    Download,
    Upload,
    Refresh,
    InfoFilled
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
      currentProviderName: '', // 当前配置的提供商名称
      apiKey: '', // API 密钥
      modelName: '', // 模型名称
      temperature: 1, // 温度参数
      topK: null, // Top K 参数
      maxTokens: null, // 最大 token 数
      topP: null, // Top P 参数
      isSaving: false, // 保存按钮加载状态
      isExporting: false, // 导出按钮加载状态
      isImporting: false, // 导入按钮加载状态
      baseUrl: '', // Base URL 输入项
      savedConfigs: {}, // 已保存的配置
      configPath: '', // 配置文件路径
      isSettingPath: false, // 设置路径按钮加载状态
      currentConfigPath: '', // 当前配置文件路径
      isBackingUp: false, // 备份按钮加载状态
      isRestoring: false, // 恢复按钮加载状态
    };
  },
  computed: {
    // 判断是否为自定义提供商
    isCustomProvider() {
      return ['硅基流动', '其他'].includes(this.currentProvider);
    }
  },
  methods: { // 组件方法
    // 加载已保存的配置列表
    async loadSavedConfigs() {
      try {
        const response = await axios.get('/saved_configs');
        if (response.data.status === 'success') {
          this.savedConfigs = response.data.configurations || {};
          this.currentProviderName = response.data.current_provider || '';
        }
      } catch (error) {
        console.error('加载已保存配置失败:', error);
        this.$message.error('加载已保存配置失败');
      }
    },
    
    // 加载指定配置到表单
    loadConfig(providerName, config) {
      this.currentProvider = providerName;
      this.apiKey = config.api_key || '';
      this.modelName = config.model || '';
      this.baseUrl = config.base_url || '';
      this.temperature = config.temperature ?? 1;
      this.topK = config.top_k || null;
      this.maxTokens = config.max_tokens || null;
      this.topP = config.top_p || null;
      
      this.$message.success(`已加载 ${providerName} 的配置`);
    },
    
    // 删除配置
    async deleteConfig(providerName) {
      try {
        await this.$confirm(`确定要删除 ${providerName} 的配置吗？`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        await axios.delete(`/config/${encodeURIComponent(providerName)}`);
        this.$message.success('配置删除成功');
        await this.loadSavedConfigs(); // 重新加载配置列表
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除配置失败:', error);
          this.$message.error('删除配置失败');
        }
      }
    },
    
    // 清空表单
    clearForm() {
      this.currentProvider = '';
      this.apiKey = '';
      this.modelName = '';
      this.baseUrl = '';
      this.temperature = 1;
      this.topK = null;
      this.maxTokens = null;
      this.topP = null;
      this.enableMCP = false;
      this.mcpConfig = '';
    },
    
    // 掩码API密钥
    maskApiKey(apiKey) {
      if (!apiKey) return '未设置';
      if (apiKey.length <= 8) return '*'.repeat(apiKey.length);
      return apiKey.substring(0, 4) + '*'.repeat(apiKey.length - 8) + apiKey.substring(apiKey.length - 4);
    },
    
    handleProviderChange() { // 处理提供商选择变化
      // 切换提供商时可以重置或加载特定配置，暂时留空
      this.apiKey = '';
      this.modelName = '';
      this.baseUrl = '';
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
      // 对自定义提供商验证base_url
      if (this.isCustomProvider && !this.baseUrl.trim()) {
        this.$message.error('请输入 API Base URL');
        return;
      }

      // 准备要发送的配置数据
      const config = {
        api_key: this.apiKey,
        model: this.modelName,
        // 只包含用户实际修改过的参数，或有值的参数
        ...(this.temperature !== null && this.temperature !== undefined && { temperature: this.temperature }),
        ...(this.topK !== null && this.topK !== undefined && { top_k: this.topK }),
        ...(this.maxTokens !== null && this.maxTokens !== undefined && { max_tokens: this.maxTokens }),
        ...(this.topP !== null && this.topP !== undefined && { top_p: this.topP }),
      };

      // 对自定义提供商添加base_url
      if (this.isCustomProvider && this.baseUrl.trim()) {
        config.base_url = this.baseUrl.trim();
      }

      this.isSaving = true; // 设置保存按钮加载状态为 true
      try {
        // 2. 发送请求到后端
        if (this.enableMCP) { // 如果启用了 MCP 模式
          // 检查MCP配置是否为空
          if (!this.mcpConfig.trim()) {
            this.$message.error('请输入MCP配置');
            return;
          }
          try {
            JSON.parse(this.mcpConfig); // 验证 MCP 配置的 JSON 格式
          } catch (e) {
            this.$message.error('MCP配置JSON格式错误: ' + e.message);
            return;
          }
          
          // 发送MCP配置保存请求
          await axios.post('/mcp/save_config', {
            provider_name: this.currentProvider,
            config: config,
            mcp_config: JSON.parse(this.mcpConfig)
          });
        } else {
          // 非MCP模式，直接发送切换提供商请求
          await axios.post('/switch_provider', {
            provider_name: this.currentProvider,
            config: config
          });
        }
        
        // 3. 成功提示并重新加载配置列表
        this.$message.success('设置保存成功！');
        await this.loadSavedConfigs(); // 重新加载配置列表
        
        // 4. 询问是否跳转到对话页面
        try {
          await this.$confirm('配置保存成功！是否跳转到对话页面？', '跳转确认', {
            confirmButtonText: '跳转',
            cancelButtonText: '继续配置',
            type: 'success'
          });
          this.$router.push('/chat'); // 跳转到聊天页面
        } catch (error) {
          // 用户选择继续配置，不做任何操作
        }
      } catch (error) {
        // 5. 错误处理
        console.error('保存失败:', error); // 打印错误信息
        let errorMsg = '保存设置失败，请检查配置或稍后再试';
        
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
          await this.loadSavedConfigs(); // 重新加载配置列表
        } catch (error) {
          console.error('导入配置失败:', error); // 打印错误信息
          this.$message.error('导入配置失败，请检查文件内容或稍后再试。'); // 显示错误提示
        } finally {
          this.isImporting = false; // 无论成功或失败，都将导入按钮加载状态设置为 false
        }
      };
      reader.readAsText(file.raw); // 读取文件内容为文本
    },
    
    // 设置配置文件路径
    async setConfigPath() {
      if (!this.configPath.trim()) {
        this.$message.error('请输入配置文件路径');
        return;
      }
      
      this.isSettingPath = true; // 设置设置路径按钮加载状态为 true
      try {
        const response = await axios.post('/set_config_path', {
          config_path: this.configPath
        });
        if (response.data.status === 'success') {
          this.currentConfigPath = response.data.config_path;
          this.$message.success('配置文件路径设置成功！');
          // 重新加载配置列表
          await this.loadSavedConfigs();
        }
      } catch (error) {
        console.error('设置配置文件路径失败:', error);
        let errorMsg = '设置配置文件路径失败，请检查路径格式或稍后再试';
        if (error.response?.data?.detail) {
          errorMsg = error.response.data.detail;
        }
        this.$message.error(errorMsg);
      } finally {
        this.isSettingPath = false; // 无论成功或失败，都将设置路径按钮加载状态设置为 false
      }
    },
    
    // 加载配置文件路径
    async loadConfigPath() {
      try {
        const response = await axios.get('/get_config_path');
        if (response.data.status === 'success') {
          this.configPath = response.data.config_path;
          this.currentConfigPath = response.data.config_path;
        }
      } catch (error) {
        console.error('加载配置文件路径失败:', error);
        this.$message.error('加载配置文件路径失败');
      }
    },
    
    // 备份配置
    async backupConfig() {
      this.isBackingUp = true; // 设置备份按钮加载状态为 true
      try {
        const response = await axios.get('/backup_config'); // 发送备份配置的请求
        if (response.data.status === 'success') {
          this.$message.success(response.data.message); // 显示成功提示
        }
      } catch (error) {
        console.error('备份配置失败:', error); // 打印错误信息
        let errorMsg = '备份配置失败，请稍后再试';
        if (error.response?.data?.detail) {
          errorMsg = error.response.data.detail;
        }
        this.$message.error(errorMsg); // 显示错误提示
      } finally {
        this.isBackingUp = false; // 无论成功或失败，都将备份按钮加载状态设置为 false
      }
    },
    
    // 恢复配置
    async handleRestoreSuccess(response, file) {
      this.isRestoring = true; // 设置恢复按钮加载状态为 true
      try {
        const config = JSON.parse(response.data); // 解析配置数据
        await axios.post('/restore_config', config); // 发送恢复配置的请求
        this.$message.success('配置恢复成功！'); // 显示成功提示
        // 恢复成功后，重新加载配置以更新 UI
        await this.loadSavedConfigs(); // 重新加载配置列表
      } catch (error) {
        console.error('恢复配置失败:', error); // 打印错误信息
        let errorMsg = '恢复配置失败，请检查文件内容或稍后再试';
        if (error.response?.data?.detail) {
          errorMsg = error.response.data.detail;
        }
        this.$message.error(errorMsg); // 显示错误提示
      } finally {
        this.isRestoring = false; // 无论成功或失败，都将恢复按钮加载状态设置为 false
      }
    },
    
    // 处理恢复配置前的检查
    beforeRestoreUpload(file) {
      const isJson = file.type === 'application/json'; // 检查是否是 JSON 文件
      if (!isJson) {
        this.$message.error('只能上传 JSON 格式的文件!'); // 提示文件格式错误
      }
      return isJson;
    },
    
    // 处理恢复配置的文件
    async handleRestoreFile(event) {
      const file = event.file; // 获取上传的文件
      const reader = new FileReader(); // 创建 FileReader 对象
      reader.onload = async (e) => { // 文件读取完成回调
        try {
          const config = JSON.parse(e.target.result); // 解析 JSON 内容
          this.isRestoring = true; // 设置恢复按钮加载状态为 true
          await this.handleRestoreSuccess(null, config); // 调用处理恢复成功的函数
        } catch (error) {
          console.error('恢复配置失败:', error); // 打印错误信息
          this.$message.error('恢复配置失败，请检查文件内容或稍后再试。'); // 显示错误提示
        } finally {
          this.isRestoring = false; // 无论成功或失败，都将恢复按钮加载状态设置为 false
        }
      };
      reader.readAsText(file); // 读取文件内容为文本
    },
    
    // 显示调试信息
    async showDebugInfo() {
      try {
        const response = await axios.get('/debug_info');
        if (response.data.status === 'success') {
          const debugInfo = response.data.debug_info;
          let message = `调试信息:\n`;
          message += `当前提供商: ${debugInfo.current_provider || '未设置'}\n`;
          message += `配置文件路径: ${debugInfo.config_file_path}\n`;
          message += `配置文件存在: ${debugInfo.config_file_exists ? '是' : '否'}\n`;
          message += `已保存配置数量: ${Object.keys(debugInfo.saved_configurations).length}\n`;
          message += `可用提供商: ${debugInfo.available_providers.join(', ') || '无'}\n`;
          
          if (debugInfo.current_provider_config) {
            message += `\n当前提供商配置:\n`;
            message += `模型: ${debugInfo.current_provider_config.model}\n`;
            message += `Base URL: ${debugInfo.current_provider_config.base_url}\n`;
            message += `API Key: ${debugInfo.current_provider_config.api_key}\n`;
            message += `Temperature: ${debugInfo.current_provider_config.temperature}\n`;
            message += `Max Tokens: ${debugInfo.current_provider_config.max_tokens}\n`;
            message += `Top P: ${debugInfo.current_provider_config.top_p}\n`;
            message += `Top K: ${debugInfo.current_provider_config.top_k}\n`;
          }
          
          this.$alert(message, '调试信息', {
            confirmButtonText: '确定',
            type: 'info',
            dangerouslyUseHTMLString: false
          });
        }
      } catch (error) {
        console.error('获取调试信息失败:', error);
        this.$message.error('获取调试信息失败');
      }
    },
  },
  
  async created() { // 组件创建后生命周期钩子
    // 加载已保存的配置
    await this.loadSavedConfigs();
    // 加载配置文件路径
    await this.loadConfigPath();
  }
};
</script>

<style scoped>
.settings-main-container {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: row;
}
.settings-content {
  flex: 1;
  margin-left: 56px; /* 预留导航栏宽度 */
  padding: 32px 0 32px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
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

/* 已保存配置卡片样式 */
.saved-configs-card {
  margin-bottom: 24px; /* 下外边距 */
  border-radius: 12px; /* 圆角 */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); /* 阴影效果 */
}

/* 卡片头部样式 */
.card-header {
  display: flex; /* 弹性布局 */
  justify-content: space-between; /* 两端对齐 */
  align-items: center; /* 垂直居中 */
}

/* 已保存配置列表样式 */
.saved-configs-list {
  display: flex; /* 弹性布局 */
  flex-direction: column; /* 垂直排列 */
  gap: 12px; /* 间距 */
}

/* 已保存配置项样式 */
.saved-config-item {
  display: flex; /* 弹性布局 */
  justify-content: space-between; /* 两端对齐 */
  align-items: center; /* 垂直居中 */
  padding: 12px; /* 内边距 */
  border: 1px solid var(--el-border-color-light); /* 边框 */
  border-radius: 8px; /* 圆角 */
  background-color: var(--el-bg-color-page); /* 背景色 */
  transition: all 0.3s ease; /* 过渡效果 */
}

.saved-config-item:hover {
  border-color: var(--el-color-primary); /* 悬停时边框颜色 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 悬停时阴影 */
}

.saved-config-item.current {
  border-color: var(--el-color-success); /* 当前配置的边框颜色 */
  background-color: var(--el-color-success-light-9); /* 当前配置的背景色 */
}

/* 配置信息样式 */
.config-info {
  flex: 1; /* 占据剩余空间 */
}

.provider-name {
  font-weight: 600; /* 字体粗细 */
  font-size: 1rem; /* 字体大小 */
  margin-bottom: 4px; /* 下外边距 */
  display: flex; /* 弹性布局 */
  align-items: center; /* 垂直居中 */
  gap: 8px; /* 间距 */
}

.config-details {
  display: flex; /* 弹性布局 */
  flex-direction: column; /* 垂直排列 */
  gap: 2px; /* 间距 */
  font-size: 0.875rem; /* 字体大小 */
  color: var(--el-text-color-secondary); /* 文本颜色 */
}

.model-name, .api-key {
  font-family: 'Fira Code', monospace; /* 等宽字体 */
}

/* 配置操作按钮样式 */
.config-actions {
  display: flex; /* 弹性布局 */
  gap: 8px; /* 间距 */
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

/* 配置文件路径设置样式 */
.config-path-section {
  margin-bottom: 24px; /* 下外边距 */
}

.section-title {
  font-size: 1.2rem; /* 字体大小 */
  font-weight: 600; /* 字体粗细 */
  margin-bottom: 8px; /* 下外边距 */
  color: var(--el-text-color-primary); /* 文本颜色 */
}

.config-path-input {
  display: flex; /* 弹性布局 */
  gap: 10px; /* 间距 */
}

.path-input {
  flex: 1; /* 占据剩余空间 */
}

.path-info {
  display: flex; /* 弹性布局 */
  justify-content: space-between; /* 两端对齐 */
  align-items: center; /* 垂直居中 */
  margin-top: 10px; /* 上外边距 */
}

.current-path {
  font-size: 0.875rem; /* 字体大小 */
  color: var(--el-text-color-secondary); /* 文本颜色 */
}

/* 备份和恢复功能样式 */
.backup-restore-section {
  margin-bottom: 24px; /* 下外边距 */
}

.subsection-title {
  font-size: 1.2rem; /* 字体大小 */
  font-weight: 600; /* 字体粗细 */
  margin-bottom: 8px; /* 下外边距 */
  color: var(--el-text-color-primary); /* 文本颜色 */
}

.backup-actions {
  display: flex; /* 弹性布局 */
  gap: 10px; /* 间距 */
}

.el-button[type="primary"], .el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
  color: #fff;
}
.el-button[type="danger"], .el-button--danger {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: #fff;
}
.el-button[type="info"], .el-button--info {
  background-color: #909399;
  border-color: #909399;
  color: #fff;
}
.el-button[type="success"], .el-button--success {
  background-color: #67c23a;
  border-color: #67c23a;
  color: #fff;
}
.el-button[type="warning"], .el-button--warning {
  background-color: #e6a23c;
  border-color: #e6a23c;
  color: #fff;
}
.el-button {
  border-radius: 8px;
  margin-right: 12px;
  margin-bottom: 8px;
  font-weight: 500;
  transition: background 0.2s, color 0.2s;
}
.el-button:last-child {
  margin-right: 0;
}
</style>