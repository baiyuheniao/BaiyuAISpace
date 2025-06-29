# Multi-LLM Management Platform / 多模态LLM管理平台

## 项目概述 | Overview
统一管理多个LLM服务提供商的中间件，支持动态配置和切换不同AI服务商。采用前后端分离架构，前端基于Vue3+ElementPlus，后端使用Python异步框架。

## 核心功能 | Features
✅ 多服务商接入（OpenAI/Anthropic/阿里云/智谱等）  
✅ 运行时动态切换服务商  
✅ 标准化API接口  
✅ 服务商配置集中管理
✅ 支持MCP功能
历史聊天记录管理
多API配置保存
多智能体配置保存
MCP调用安全机制

## 技术栈 | Tech Stack
**前端**  
`Vue3` `ElementPlus` `Axios` `Vue-Router`

**后端**  
`Python 3.10+` `FastAPI` `AsyncIO` `Pydantic`

## 快速启动 | Installation
```bash
# 后端服务
pip install -r requirements.txt
uvicorn server:app --reload

# 前端服务
cd frontend
pnpm install
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
