# Antigravity Controller

Discord Bot for remote coding assistance via Gemini AI. Control your coding projects from your phone through Discord.

## Features

- **AI-Powered Coding**: Natural language interaction powered by Gemini API
- **File Operations**: Read, write, search, and browse project files
- **Git Management**: Status, diff, log, commit, and push
- **Command Execution**: Run tests, builds, linters from Discord
- **Project Inspection**: Tree structure, file info, TODO finder
- **Security**: Path whitelisting + confirmation for dangerous operations

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

### Setup

```bash
# Install
cd antigravity-controller
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your tokens
```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application", name it "Antigravity"
3. Go to "Bot" tab, click "Add Bot"
4. Copy the Token -> paste into `.env` as `DISCORD_TOKEN`
5. Enable **Message Content Intent** under "Privileged Gateway Intents"
6. Go to "OAuth2" -> "URL Generator"
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
7. Copy the generated URL -> open in browser -> add bot to your server
8. Copy your Server ID -> paste into `.env` as `DISCORD_GUILD_ID`

### Run

```bash
python -m controller.main
```

### Usage

Mention the bot or send a DM:

- `@Antigravity show me the project structure of /path/to/project`
- `@Antigravity read src/main.py`
- `@Antigravity what's the git status?`
- `@Antigravity run pytest`
- `@Antigravity find all TODOs`

Slash commands: `/status`, `/clear`, `/help`

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
- **Confirmation**: Dangerous operations (write, execute, push) require Approve/Deny button click
- **Path Traversal Protection**: Resolves symlinks, blocks `..` traversal

## Development

```bash
# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/
```

## License

Apache-2.0