# 测试文件说明

这个目录包含了项目的各种测试文件，用于验证功能的正确性和稳定性。

## 📁 目录结构

```
tests/
├── README.md                    # 本文档
├── api_tests/                   # API测试
│   ├── test_openai.py          # OpenAI API测试
│   ├── test_anthropic.py       # Anthropic API测试
│   └── test_custom_apis.py     # 自定义API测试
├── layout_tests/                # 布局测试
│   ├── test_responsive.html    # 响应式布局测试
│   ├── test_sidebar.html       # 侧边栏功能测试
│   └── test_animations.html    # 动画效果测试
└── integration_tests/           # 集成测试
    ├── test_config_management.py # 配置管理功能测试
    ├── test_chat_functionality.py # 聊天功能测试
    └── test_data_persistence.py  # 数据持久化测试
```

## 🧪 测试类型

### API测试 (`api_tests/`)
- **目的**: 验证各种API服务商的连接和响应
- **内容**: 
  - API密钥验证
  - 请求/响应格式检查
  - 错误处理测试
  - 超时设置验证
- **运行方式**: `python test_*.py`

### 布局测试 (`layout_tests/`)
- **目的**: 验证前端界面的响应式和交互功能
- **内容**:
  - 响应式布局测试
  - 侧边栏展开/折叠测试
  - 动画效果验证
  - 不同屏幕尺寸适配
- **运行方式**: 在浏览器中打开HTML文件

### 集成测试 (`integration_tests/`)
- **目的**: 验证前后端功能的完整性和数据交互
- **内容**:
  - 配置管理功能测试
  - 聊天功能端到端测试
  - 数据持久化验证
  - 用户交互流程测试
- **运行方式**: `python test_*.py`

## 📋 测试文件说明

### `test_config_management.py`
- **位置**: `integration_tests/`
- **功能**: 测试多份API配置的管理功能
- **测试内容**:
  - 配置保存功能
  - 配置编辑功能
  - 配置切换功能
  - 配置删除功能
- **运行前准备**: 确保后端服务器已启动
- **运行命令**: `python test_config_management.py`

## 🔧 运行测试

### 环境准备
1. 确保Python环境已安装
2. 安装必要的依赖包：`pip install requests`
3. 启动后端服务器：`python server.py`

### 运行API测试
```bash
cd docs/tests/api_tests
python test_openai.py
python test_anthropic.py
```

### 运行集成测试
```bash
cd docs/tests/integration_tests
python test_config_management.py
```

### 运行布局测试
1. 在浏览器中打开 `docs/tests/layout_tests/` 目录下的HTML文件
2. 手动测试各种交互功能
3. 检查在不同屏幕尺寸下的表现

## 📊 测试结果

### 通过标准
- ✅ API连接成功，响应正常
- ✅ 界面布局正确，响应式适配良好
- ✅ 功能交互流畅，无错误提示
- ✅ 数据保存和读取正常

### 失败处理
- ❌ 检查网络连接和API密钥
- ❌ 查看浏览器控制台错误信息
- ❌ 检查后端服务器日志
- ❌ 验证配置文件格式

## 📝 添加新测试

### 创建API测试
1. 在 `api_tests/` 目录下创建新的测试文件
2. 使用 `requests` 库发送HTTP请求
3. 验证响应状态码和数据格式
4. 添加错误处理测试

### 创建布局测试
1. 在 `layout_tests/` 目录下创建HTML文件
2. 包含必要的CSS和JavaScript
3. 模拟各种用户交互场景
4. 测试响应式布局效果

### 创建集成测试
1. 在 `integration_tests/` 目录下创建Python文件
2. 测试完整的功能流程
3. 验证前后端数据交互
4. 检查数据持久化效果

## 🚀 持续集成

建议将测试文件集成到CI/CD流程中：
- 每次代码提交时自动运行测试
- 生成测试报告和覆盖率统计
- 在测试失败时阻止代码合并
- 定期运行完整的测试套件 