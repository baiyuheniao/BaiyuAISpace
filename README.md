# BaiyuAISpace - 多模态LLM管理平台

一个功能强大的多模态LLM管理平台，支持多种AI服务商，提供前后端分离的架构，支持动态切换服务商和本地配置持久化存储。

## 🚀 主要功能

### 核心功能
- **多服务商支持**: 支持OpenAI、Anthropic、阿里云、智谱、硅基流动等多种AI服务商
- **动态切换**: 无需重启即可动态切换不同的AI服务商
- **本地配置持久化**: 配置信息自动保存到本地，重启后无需重新配置
- **配置管理**: 支持多套配置的保存、加载、删除和管理
- **配置备份恢复**: 支持配置的备份和恢复功能

### 本地存储功能
- **自动保存**: 用户配置自动保存到本地JSON文件
- **配置列表**: 显示所有已保存的配置，支持快速加载和切换
- **配置路径自定义**: 用户可以自定义配置文件的存储位置
- **配置备份**: 支持配置的自动备份，包含时间戳
- **配置恢复**: 支持从备份文件恢复配置
- **安全存储**: API密钥等敏感信息安全存储在本地

## 🛠️ 技术架构

### 后端 (Python FastAPI)
- **FastAPI**: 现代化的Python Web框架
- **异步处理**: 支持高并发的异步请求处理
- **适配器模式**: 统一的API适配器接口
- **本地存储**: JSON格式的配置文件持久化

### 前端 (Vue 3 + Element Plus)
- **Vue 3**: 现代化的前端框架
- **Element Plus**: 美观的UI组件库
- **响应式设计**: 适配不同屏幕尺寸
- **实时更新**: 配置变更实时反映到界面

## 📁 项目结构

```
BaiyuAISpace/
├── server.py              # FastAPI后端服务器
├── mcp_module.py          # MCP核心模块，管理服务商和配置
├── api_adapter.py         # API适配器，支持多种服务商
├── mcp_config.json        # 本地配置文件（自动生成）
├── requirements.txt       # Python依赖
├── frontend/              # Vue3前端项目
│   ├── src/
│   │   ├── App.vue        # 主应用组件
│   │   ├── main.js        # 应用入口
│   │   ├── router/        # 路由配置
│   │   └── views/         # 页面组件
│   │       ├── ChatView.vue      # 聊天界面
│   │       └── SettingsView.vue  # 设置界面
│   ├── package.json       # 前端依赖
│   └── pnpm-lock.yaml     # 依赖锁定文件
├── docs/                  # 文档和测试文件目录
│   ├── README.md          # 文档目录说明
│   ├── API_COMPLIANCE_REPORT.md  # API合规性检查报告
│   ├── LAYOUT_FIXES.md    # 布局修复说明
│   ├── tests/             # 测试文件目录
│   │   ├── api_tests/     # API测试文件
│   │   ├── layout_tests/  # 布局测试文件
│   │   └── integration_tests/ # 集成测试文件
│   └── reports/           # 修复报告目录
│       ├── bug_fixes/     # Bug修复报告
│       ├── feature_updates/ # 功能更新报告
│       └── performance_improvements/ # 性能优化报告
└── README.md              # 项目说明文档
```

## 📚 文档说明

项目包含完整的文档和测试文件，位于 `docs/` 目录中：

- **API合规性检查报告**: 详细检查了所有API服务商适配器的合规性
- **布局修复说明**: 记录了聊天界面布局问题的修复过程
- **测试文件**: 包含API测试、布局测试和集成测试
- **修复报告**: 记录Bug修复、功能更新和性能优化的详细过程

更多详细信息请查看 [docs/README.md](./docs/README.md)。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- pnpm (推荐) 或 npm

### 最新修复 (2025-01-XX)
- ✅ 修复了阿里云通义千问适配器API调用不合规问题 ([Issue #1](https://github.com/baiyuheniao/BaiyuAISpace/issues/1))
  - 修正API端点路径为官方规范
  - 调整请求体结构，messages作为顶层字段
  - 修正响应解析逻辑，符合官方API格式

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/baiyuheniao/BaiyuAiSpace
cd BaiyuAISpace
```

2. **安装后端依赖**
```bash
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
cd frontend
pnpm install
```

4. **启动后端服务**
```bash
# 在项目根目录
python server.py
```

5. **启动前端服务**
```bash
cd frontend
pnpm run serve
```

6. **访问应用**
打开浏览器访问 `http://localhost:8080`

## 📋 使用指南

### 配置AI服务商

1. **访问设置页面**: 点击导航栏的"设置"按钮
2. **选择服务商**: 从下拉列表中选择您要配置的AI服务商
3. **填写配置信息**:
   - API密钥 (必填)
   - 模型名称 (必填)
   - 基础URL (仅自定义服务商需要)
   - 模型参数 (可选)
4. **保存配置**: 点击"保存设置"按钮

### 管理已保存的配置

1. **查看配置列表**: 在设置页面顶部可以看到所有已保存的配置
2. **加载配置**: 点击配置项右侧的"加载"按钮快速加载配置
3. **删除配置**: 点击"删除"按钮移除不需要的配置
4. **切换当前配置**: 当前使用的配置会显示"当前"标签

### 配置文件管理

1. **自定义存储路径**: 在设置页面可以自定义配置文件的存储位置
2. **备份配置**: 点击"备份配置"按钮创建配置备份
3. **恢复配置**: 点击"恢复配置"按钮从备份文件恢复配置

### 开始聊天

1. **配置完成**: 确保已正确配置至少一个AI服务商
2. **访问聊天页面**: 点击导航栏的"聊天"按钮
3. **开始对话**: 在输入框中输入消息，按回车或点击发送按钮

## 🔧 配置说明

### 支持的AI服务商

| 服务商 | 配置项 | 说明 |
|--------|--------|------|
| OpenAI | API Key, Model | 支持GPT系列模型 |
| Anthropic | API Key, Model | 支持Claude系列模型 |
| 阿里云 | API Key, Model | 支持通义千问系列模型 |
| 智谱 | API Key, Model | 支持ChatGLM系列模型 |
| 硅基流动 | API Key, Base URL, Model | 自定义API端点 |
| 其他 | API Key, Base URL, Model | 通用自定义配置 |

### 模型参数

- **Temperature**: 控制输出的随机性 (0-2)
- **Max Tokens**: 最大输出token数
- **Top K**: 采样时考虑的top-k个token
- **Top P**: 核采样参数 (0-1)

## 🔒 安全说明

- API密钥等敏感信息仅存储在本地
- 配置文件使用JSON格式，便于查看和编辑
- 支持配置文件的备份和恢复
- 建议定期备份重要配置

## 🐛 故障排除

### 常见问题

1. **配置保存失败**
   - 检查API密钥是否正确
   - 确认模型名称是否有效
   - 查看后端日志获取详细错误信息

2. **聊天请求失败**
   - 确认当前服务商配置正确
   - 检查网络连接
   - 验证API配额是否充足

3. **配置文件加载失败**
   - 检查配置文件路径是否正确
   - 确认文件权限
   - 验证JSON格式是否正确

### 日志查看

后端日志会输出到控制台，包含详细的错误信息和调试信息。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用AGPL3.0许可证。
本项目采用 GNU Affero 通用公共许可证第3版（AGPL-3.0）。  
详情请见 [LICENSE](./LICENSE) 文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至baiyuheniao@gmail.com

---

**注意**: 请确保遵守各AI服务商的使用条款和API限制。对于所有因使用本软件而造成的违法行为的后果，Baiyu不承担任何责任！

## 项目概述 | Overview
统一管理多个LLM服务提供商的中间件，支持动态配置和切换不同AI服务商。采用前后端分离架构，前端基于Vue3+ElementPlus，后端使用Python异步框架。

## 核心功能 | Features
✅ 多服务商接入（OpenAI/Anthropic/阿里云/智谱等）  
✅ 运行时动态切换服务商  
✅ 标准化API接口  
✅ 服务商配置集中管理
✅ 支持MCP功能
✅ 历史聊天记录管理
✅ 多API配置保存
/多智能体配置保存
/MCP调用安全机制
/原生自带文件调用、联网搜索
/

## 技术栈 | Tech Stack
**前端**  
`Vue3` `ElementPlus` `Axios` `Vue-Router`

**后端**  
`Python 3.10+` `FastAPI` `AsyncIO` `Pydantic`

## 快速启动 | Installation
```bash
# 后端服务
pip install -r requirements.txt(执行过一次即可)
uvicorn server:app --reload

# 前端服务
cd frontend
pnpm install(执行过一次即可)
pnpm run serve
```

## Git 提交之旅回顾与问题总结

这次项目的 Git 提交过程可谓一波三折，但最终我们都成功解决了！为了给后来的开发者提供一些经验，特此记录下我们遇到的问题以及解决方案。

### 1. 历史不相关合并问题 (`fatal: refusing to merge unrelated histories`)

**问题描述**：当本地仓库和远程仓库的提交历史完全不相关时（例如，远程仓库初始化时没有本地文件，或者本地仓库是从一个完全不同的起点开始的），直接 `git pull` 会报错 `fatal: refusing to merge unrelated histories`。

**解决方案**：使用 `--allow-unrelated-histories` 选项强制合并。

```bash
git pull origin main --allow-unrelated-histories
```

**注意事项**：此操作会合并两个不相关的历史，可能会引入大量冲突。请务必在执行前确认，并准备好解决冲突。

### 2. 合并冲突解决

**问题描述**：在执行 `git pull` 或 `git merge` 后，如果本地和远程对同一文件的同一部分进行了不同的修改，就会产生合并冲突。

**解决方案**：

1.  **识别冲突文件**：Git 会在冲突文件中标记出冲突区域（通常以 `<<<<<<<`，`=======`，`>>>>>>>` 标识）。
2.  **手动解决冲突**：打开冲突文件，根据需要保留本地或远程的修改，或者进行新的修改。删除所有冲突标记。
3.  **处理二进制文件**：对于像 `__pycache__` 这样的二进制文件或生成文件，通常不应该进行版本控制。建议将其添加到 `.gitignore` 文件中，并从 Git 索引中移除。
    ```bash
    echo '__pycache__/' >> .gitignore
    git rm -r --cached __pycache__/
    ```
    对于 `pnpm-lock.yaml` 这类锁定文件，通常应该保留，但如果冲突严重且确定远程版本是正确的，可以考虑直接使用远程版本：
    ```bash
    git checkout --theirs frontend/pnpm-lock.yaml
    ```
4.  **添加解决后的文件**：将解决冲突后的文件添加到暂存区。
    ```bash
    git add .
    ```
5.  **完成合并提交**：执行 `git commit`。此时 Git 会打开一个文本编辑器（如 Vim）让您输入合并提交信息。输入信息后保存并退出编辑器。
    *   **Vim 操作指南**：
        *   进入编辑模式：按 `i` 键。
        *   输入提交信息。
        *   退出编辑模式：按 `Esc` 键。
        *   保存并退出：输入 `:wq` 后按回车。
        *   不保存退出：输入 `:q!` 后按回车。

### 3. Git 代理配置 (`Recv failure: Connection was reset`)

**问题描述**：在某些网络环境下，直接连接 GitHub 可能会出现 `fatal: unable to access 'https://github.com/baiyuheniao/BaiyuAISpace.git/': Recv failure: Connection was reset` 等网络连接错误。

**解决方案**：配置 Git 代理。

1.  **检查代理软件**：确保您的本地代理软件（如 Clash、V2Ray 等）正在运行，并知道其 HTTP 或 SOCKS5 代理端口（例如 `7890`）。
2.  **配置本地仓库代理**：为当前 Git 仓库配置代理。请根据您的代理类型选择以下命令：
    *   **HTTP/HTTPS 代理**：
        ```bash
        git config --local http.proxy http://127.0.0.1:7890
        git config --local https.proxy http://127.0.0.1:7890
        ```
    *   **SOCKS5 代理**：
        ```bash
        git config --local http.proxy socks5://127.0.0.1:7890
        git config --local https.proxy socks5://127.0.0.1:7890
        ```
3.  **验证代理配置**：检查代理是否已成功配置。
    ```bash
    git config --local --get http.proxy
    git config --local --get https.proxy
    ```
    如果需要取消代理，可以使用：
    ```bash
    git config --local --unset http.proxy
    git config --local --unset https.proxy
    ```

### 4. 推送代码

**问题描述**：在所有问题解决后，需要将本地代码推送到远程仓库。

**解决方案**：使用 `git push -u origin main` 命令。

```bash
git push -u origin main
```

**解释**：
*   `-u` (或 `--set-upstream`) 选项会将本地的 `main` 分支与远程的 `origin/main` 分支关联起来，这样以后您只需执行 `git push` 或 `git pull` 即可。
*   `origin` 是远程仓库的别名。
*   `main` 是您要推送的本地分支。

希望这份记录能帮助到未来的你，少走弯路！🚀

## 配置说明

### 前端配置

- **当前提供商**: 选择当前使用的API服务提供商。
- **API密钥**: 输入您所选提供商的API密钥。
- **模型名称**: 输入您希望调用的模型名称。
- **Temperature**: 控制模型输出的随机性，值越大越随机。
- **Top K**: 从Top K个最高概率的词中进行采样。
- **Max Tokens**: 限制模型生成响应的最大token数量。
- **MCP模式**: 用于切换是否启用多路并发处理（Multi-Concurrent Processing）模式。
- **MCP配置**: 在MCP模式下，用户可以在此输入JSON格式的配置，用于定义不同服务提供商的详细参数。例如：`{ &quot;provider_name&quot;: { &quot;api_key&quot;: &quot;your_api_key&quot;, &quot;model_name&quot;: &quot;your_model_name&quot; } }`。请注意，JSON字符串中的双引号需要转义为`&quot;`。

### 后端配置

后端配置主要通过 `server.py` 和 `mcp_module.py` 进行管理。您可以通过修改 `mcp_module.py` 中的适配器配置来支持更多LLM服务。
