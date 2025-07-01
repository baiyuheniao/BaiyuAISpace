# BaiyuAISpace - Multi-Modal LLM Management Platform

A powerful multi-modal LLM management platform that supports multiple AI service providers, featuring a frontend-backend separated architecture with dynamic provider switching and local configuration persistence.

## 🚀 Key Features

### Core Features
- **Multi-Provider Support**: Supports OpenAI, Anthropic, Alibaba Cloud, Zhipu, SiliconFlow, and other AI service providers
- **Dynamic Switching**: Switch between different AI providers without restarting the application
- **Standardized API Interface**: Unified interface for different AI service providers
- **Provider Configuration Management**: Centralized management of provider configurations
- **MCP Support**: Model Context Protocol functionality
- **Chat History Management**: Local storage and management of chat history
- **Multi-API Configuration**: Save and manage multiple API configurations
- **Multi-Agent Configuration**: Save and manage multiple agent configurations
- **MCP Security Mechanism**: Secure MCP calling mechanism
- **Native File Support**: Built-in file calling and web search capabilities
- **Multi-format Support**: Support for various file formats (images, videos, if the called model supports them)

(Some of them have not been applying yet!!!)

### Local Storage Features
- **Auto-Save**: User configurations automatically saved to local JSON files
- **Configuration List**: Display all saved configurations with quick load and switch capabilities
- **Custom Storage Path**: Users can customize the storage location of configuration files
- **Configuration Backup**: Automatic configuration backup with timestamps
- **Configuration Recovery**: Restore configurations from backup files
- **Secure Storage**: API keys and sensitive information securely stored locally

## 🛠️ Technical Architecture

### Backend (Python FastAPI)
- **FastAPI**: Modern Python web framework
- **Asynchronous Processing**: High-concurrency async request handling
- **Adapter Pattern**: Unified API adapter interface
- **Local Storage**: JSON format configuration persistence

### Frontend (Vue 3 + Element Plus)
- **Vue 3**: Modern frontend framework
- **Element Plus**: Beautiful UI component library
- **Responsive Design**: Adapts to different screen sizes
- **Real-time Updates**: Configuration changes reflected in real-time

## 📁 Project Structure

```
BaiyuAISpace/
├── server.py              # FastAPI backend server
├── mcp_module.py          # MCP core module, manages providers and configurations
├── api_adapter.py         # API adapter, supports multiple providers
├── mcp_config.json        # Local configuration file (auto-generated)
├── requirements.txt       # Python dependencies
├── frontend/              # Vue3 frontend project
│   ├── src/
│   │   ├── App.vue        # Main application component
│   │   ├── main.js        # Application entry point
│   │   ├── router/        # Routing configuration
│   │   └── views/         # Page components
│   │       ├── ChatView.vue      # Chat interface
│   │       └── SettingsView.vue  # Settings interface
│   ├── package.json       # Frontend dependencies
│   └── pnpm-lock.yaml     # Dependency lock file
└── README.md              # Project documentation
```

## 🚀 Quick Start

### Requirements
- Python 3.8+
- Node.js 16+
- pnpm (recommended) or npm

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/baiyuheniao/BaiyuAiSpace
cd BaiyuAISpace
```

2. **Install backend dependencies**
```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
cd frontend
pnpm install
```

4. **Start the backend server**
```bash
# In the project root directory
python server.py
```

5. **Start the frontend server**
```bash
cd frontend
pnpm run serve
```

6. **Access the application**
Open your browser and visit `http://localhost:8080`

## 📋 User Guide

### Configuring AI Service Providers

1. **Access Settings Page**: Click the "Settings" button in the navigation bar
2. **Select Provider**: Choose the AI service provider you want to configure from the dropdown list
3. **Fill Configuration Information**:
   - API Key (required)
   - Model Name (required)
   - Base URL (only needed for custom providers)
   - Model Parameters (optional)
4. **Save Configuration**: Click the "Save Settings" button

### Managing Saved Configurations

1. **View Configuration List**: All saved configurations are displayed at the top of the settings page
2. **Load Configuration**: Click the "Load" button next to a configuration to quickly load it
3. **Delete Configuration**: Click the "Delete" button to remove unwanted configurations
4. **Switch Current Configuration**: The currently used configuration will show a "Current" label

### Configuration File Management

1. **Custom Storage Path**: You can customize the storage location of configuration files in the settings page
2. **Backup Configuration**: Click "Backup Configuration" to create a configuration backup
3. **Restore Configuration**: Click "Restore Configuration" to restore from a backup file

### Starting a Chat

1. **Complete Configuration**: Ensure at least one AI service provider is properly configured
2. **Access Chat Page**: Click the "Chat" button in the navigation bar
3. **Start Conversation**: Enter your message in the input box and press Enter or click the send button

## 🔧 Configuration Guide

### Supported AI Service Providers

| Provider | Configuration Items | Description |
|----------|-------------------|-------------|
| OpenAI | API Key, Model | Supports GPT series models |
| Anthropic | API Key, Model | Supports Claude series models |
| Alibaba Cloud | API Key, Model | Supports Tongyi Qianwen series models |
| Zhipu | API Key, Model | Supports ChatGLM series models |
| SiliconFlow | API Key, Base URL, Model | Custom API endpoints |
| Others | API Key, Base URL, Model | Universal custom configuration |

### Model Parameters

- **Temperature**: Controls output randomness (0-2)
- **Max Tokens**: Maximum output token count
- **Top K**: Number of top-k tokens to consider during sampling
- **Top P**: Nucleus sampling parameter (0-1)

## 🔒 Security Information

- API keys and sensitive information are stored locally only
- Configuration files use JSON format for easy viewing and editing
- Support for configuration file backup and recovery
- Regular backup of important configurations is recommended

## 🐛 Troubleshooting

### Common Issues

1. **Configuration Save Failure**
   - Check if the API key is correct
   - Verify if the model name is valid
   - Check backend logs for detailed error information

2. **Chat Request Failure**
   - Ensure current provider configuration is correct
   - Check network connection
   - Verify API quota availability

3. **Configuration File Load Failure**
   - Check if the configuration file path is correct
   - Verify file permissions
   - Validate JSON format

### Log Viewing

Backend logs are output to the console, containing detailed error information and debug messages.

## 🤝 Contributing

We welcome Issues and Pull Requests to improve the project!

## 📄 License

This project is licensed under the AGPL-3.0 License.
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
For details, see the [LICENSE](./LICENSE) file.

## 📞 Contact

For questions or suggestions, please contact us through:
- Submit a GitHub Issue
- Send email to baiyuheniao@gmail.com

---

**Note**: Please ensure compliance with the terms of service and API limitations of each AI service provider. Baiyu is not responsible for any consequences of illegal activities caused by using this software! 