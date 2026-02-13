# Antigravity Controller

Discord Bot for remote coding assistance via Gemini AI. Control your coding projects from your phone through Discord.

[中文版本](#中文说明)

## Features

- **AI-Powered Coding**: Natural language interaction powered by Gemini API
- **File Operations**: Read, write, search, and browse project files
- **Git Management**: Status, diff, log, commit, and push
- **Command Execution**: Run tests, builds, linters from Discord
- **Project Inspection**: Tree structure, file info, TODO finder
- **Security**: Path whitelisting + confirmation buttons for dangerous operations

## Architecture

```
Phone (Discord App)
    | Discord API
Discord Bot (Python service on your machine)
    |
Gemini API (AI) + Local Tools (file/git/shell)
    |
Your Project Files
```

## Quick Start

### Prerequisites

- Python 3.11+
- [Discord Bot Token](https://discord.com/developers/applications)
- [Gemini API Key](https://aistudio.google.com/)

### Installation

```bash
cd antigravity-controller
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Edit .env with your tokens
```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**, name it (e.g. "Antigravity")
3. Go to **"Bot"** tab -> Click **"Add Bot"**
4. Copy the Token -> paste into `.env` as `DISCORD_TOKEN`
5. Enable **"MESSAGE CONTENT INTENT"** under "Privileged Gateway Intents"
6. Go to **"OAuth2"** -> **"URL Generator"**
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Message History`
7. Copy the generated URL -> open in browser -> add bot to your server
8. Right-click your server name -> **"Copy Server ID"** -> paste into `.env` as `DISCORD_GUILD_ID`
   - (Requires Developer Mode: User Settings -> Advanced -> Developer Mode)

### Run

```bash
python -m controller.main
```

## User Guide

### Talking to the Bot

There are two ways to interact with the bot:

- **Mention**: In any channel, type `@Antigravity` followed by your message
- **Direct Message (DM)**: Send a private message to the bot directly

The bot understands natural language. Just describe what you want to do.

### Example Commands

**Project Overview:**
```
@Antigravity show me the project structure of /Users/me/my-project
@Antigravity find all TODOs in /Users/me/my-project
```

**Reading Code:**
```
@Antigravity read the file /Users/me/my-project/src/main.py
@Antigravity search for "def process" in /Users/me/my-project
```

**Git Operations:**
```
@Antigravity what's the git status of /Users/me/my-project?
@Antigravity show me the recent git log
@Antigravity show the diff of uncommitted changes
```

**Running Commands (requires approval):**
```
@Antigravity run pytest in /Users/me/my-project
@Antigravity run ruff check src/ in /Users/me/my-project
```

**Writing Code (requires approval):**
```
@Antigravity create a file /Users/me/my-project/src/utils.py with a function to parse JSON
@Antigravity add error handling to /Users/me/my-project/src/main.py
```

### Confirmation System

Dangerous operations display **Approve** / **Deny** buttons. You must click a button within 60 seconds:

| Operation | Requires Confirmation |
|-----------|----------------------|
| Read file | No |
| List directory | No |
| Git status/diff/log | No |
| **Write file** | **Yes** |
| **Run command** | **Yes** |
| **Git commit** | **Yes** |
| **Git push** | **Yes** |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/status` | Show bot configuration and allowed directories |
| `/clear` | Clear conversation history for this channel |
| `/help` | Show usage help |

### Conversation Memory

The bot remembers context within each channel. You can have multi-turn conversations:

```
You:  @Antigravity read /Users/me/project/main.py
Bot:  [shows file content]
You:  @Antigravity add logging to the main function
Bot:  [confirms and writes updated file]
```

Use `/clear` to reset the conversation when switching topics.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Bot token (required) | - |
| `DISCORD_GUILD_ID` | Server ID for faster command sync | - |
| `GEMINI_API_KEY` | Gemini API key (required) | - |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `ALLOWED_DIRECTORIES` | Comma-separated allowed paths (required) | - |
| `ALLOWED_USER_IDS` | Comma-separated Discord user IDs (empty = all) | - |
| `REQUIRE_CONFIRMATION` | Confirm dangerous operations | `true` |
| `MAX_FILE_SIZE_KB` | Max file size for read/write | `500` |
| `COMMAND_TIMEOUT_SECONDS` | Shell command timeout | `30` |

## Security

- **Path Whitelist**: Only operates within `ALLOWED_DIRECTORIES`
- **User Authorization**: Optional `ALLOWED_USER_IDS` restriction
- **Confirmation Buttons**: Dangerous operations require Approve/Deny click
- **Path Traversal Protection**: Resolves symlinks, blocks `..` traversal
- **Command Timeout**: Shell commands auto-terminate after configured timeout

## Development

```bash
pytest tests/ -v        # Run tests
ruff check src/ tests/  # Lint
```

## License

Apache-2.0

---

# 中文说明

通过 Discord 远程控制你的编程项目，由 Gemini AI 驱动的编程助手。

## 功能特性

- **AI 驱动编程**：通过自然语言与 Gemini API 交互
- **文件操作**：读取、写入、搜索、浏览项目文件
- **Git 管理**：status、diff、log、commit、push
- **命令执行**：在 Discord 中运行测试、构建、代码检查
- **项目检查**：目录树、文件信息、TODO 搜索
- **安全机制**：路径白名单 + 危险操作确认按钮

## 快速开始

### 前置要求

- Python 3.11+
- [Discord Bot Token](https://discord.com/developers/applications)
- [Gemini API Key](https://aistudio.google.com/)

### 安装

```bash
cd antigravity-controller
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# 编辑 .env 填入你的 Token
```

### Discord Bot 设置

1. 打开 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 **"New Application"**，输入名称（如 "Antigravity"）
3. 进入 **"Bot"** 选项卡 -> 点击 **"Add Bot"**
4. 复制 Token -> 填入 `.env` 的 `DISCORD_TOKEN`
5. 在 "Privileged Gateway Intents" 下开启 **"MESSAGE CONTENT INTENT"**
6. 进入 **"OAuth2"** -> **"URL Generator"**
   - Scopes 勾选：`bot`、`applications.commands`
   - Bot Permissions 勾选：`Send Messages`、`Read Message History`
7. 复制生成的 URL -> 在浏览器打开 -> 将 Bot 添加到你的服务器
8. 右键服务器名称 -> **"Copy Server ID"** -> 填入 `.env` 的 `DISCORD_GUILD_ID`
   - （需要先开启开发者模式：用户设置 -> 高级 -> 开发者模式）

### 运行

```bash
python -m controller.main
```

## 使用指南

### 与 Bot 对话

两种方式：
- **@提及**：在任意频道输入 `@Antigravity` 加上你的请求
- **私信 (DM)**：直接给 Bot 发私信

Bot 理解自然语言，直接描述你要做什么即可。

### 示例

```
@Antigravity 显示 /Users/me/my-project 的项目结构
@Antigravity 读取 /Users/me/my-project/src/main.py
@Antigravity 查看 git status
@Antigravity 运行 pytest
@Antigravity 给 main.py 添加错误处理
@Antigravity 查找所有 TODO
```

### 确认机制

危险操作会弹出 **Approve** / **Deny** 按钮，需在 60 秒内点击：

| 操作 | 需要确认 |
|------|---------|
| 读取文件 | 否 |
| 列出目录 | 否 |
| Git status/diff/log | 否 |
| **写入文件** | **是** |
| **执行命令** | **是** |
| **Git commit** | **是** |
| **Git push** | **是** |

### Slash 命令

| 命令 | 说明 |
|------|------|
| `/status` | 显示 Bot 配置和允许的目录 |
| `/clear` | 清除当前频道的对话历史 |
| `/help` | 显示使用帮助 |

## 配置项

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DISCORD_TOKEN` | Bot Token（必填） | - |
| `DISCORD_GUILD_ID` | 服务器 ID | - |
| `GEMINI_API_KEY` | Gemini API Key（必填） | - |
| `GEMINI_MODEL` | Gemini 模型名称 | `gemini-2.5-flash` |
| `ALLOWED_DIRECTORIES` | 允许访问的目录，逗号分隔（必填） | - |
| `ALLOWED_USER_IDS` | 允许的 Discord 用户 ID，逗号分隔（空=所有人） | - |
| `REQUIRE_CONFIRMATION` | 危险操作是否需要确认 | `true` |
| `MAX_FILE_SIZE_KB` | 最大文件大小 (KB) | `500` |
| `COMMAND_TIMEOUT_SECONDS` | 命令执行超时 (秒) | `30` |

## 安全机制

- **路径白名单**：只允许操作 `ALLOWED_DIRECTORIES` 内的文件
- **用户授权**：可选的 `ALLOWED_USER_IDS` 限制
- **确认按钮**：危险操作需点击 Approve/Deny
- **路径穿越防护**：解析符号链接，阻止 `..` 路径穿越
- **命令超时**：Shell 命令超时自动终止

## 开发

```bash
pytest tests/ -v        # 运行测试
ruff check src/ tests/  # 代码检查
```

## 许可证

Apache-2.0