# Downcode

A lightweight, powerful AI coding agent that works with any OpenAI-compatible API.

## Features

- OpenAI-compatible API support (NVIDIA API, OpenAI, local models, etc.)
- Auto-discovers relevant files from git changes
- Multi-tool support: bash, read, write, edit, view
- No arbitrary limits (file size, line count, etc.)
- Streaming responses support
- Persistent sessions
- Simple, readable Python code (~200 lines)

## Installation

```bash
# Clone the repository
git clone https://github.com/coursexwagon/Downcode.git
cd Downcode

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### NVIDIA API Setup

```bash
export NVIDIA_API_KEY="your-nvidia-api-key"
export NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1"
export NVIDIA_MODEL="meta/llama-3.1-405b-instruct"  # or other model
```

### OpenAI Setup

```bash
export OPENAI_API_KEY="your-openai-key"
export NVIDIA_MODEL="gpt-4"  # or gpt-3.5-turbo, etc.
```

### Local Model Setup (via LiteLLM)

```bash
export NVIDIA_BASE_URL="http://localhost:8000/v1"
export NVIDIA_API_KEY="sk-xxx"  # any key for local
export NVIDIA_MODEL="local-model-name"
```

## Usage

```bash
# Run with default settings
python downcode.py "fix the bug in main.py"

# Run with specific model
python downcode.py "add error handling" --model meta/llama-3.1-70b-instruct

# Run with local LLM
python downcode.py "refactor utils.py" --base-url http://localhost:8000/v1 --api-key sk-any
```

## Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `bash` | Run shell commands | `ls -la`, `python test.py` |
| `read` | Read file contents | `{"file_path": "main.py"}` |
| `write` | Write new file | `{"file_path": "new.py", "content": "..."}` |
| `edit` | Edit file (search/replace) | `{"file_path": "main.py", "old_string": "...", "new_string": "..."}` |
| `view` | List directory contents | `{"dir_path": "."}` |
| `done` | Complete the task | `{"summary": "Added error handling"}` |

## How It Works

1. **Context Discovery**: Automatically finds modified files in your git repo
2. **Tool Loop**: Agent iteratively decides which tool to use
3. **Execution**: Runs bash commands, reads/writes files, etc.
4. **Completion**: Returns when task is done or max iterations reached

## Example Session

```
$ python downcode.py "add logging to the API"

🤖 Downcode using meta/llama-3.1-405b-instruct
📁 Found 5 relevant files
==================================================

🔧 Tool: view
📤 Result: 📁 src/
             📄 api.py (2456 bytes)
             📄 auth.py (892 bytes)
             📄 utils.py (412 bytes)

🔧 Tool: read
📤 Result: import requests ...

🔧 Tool: edit
📤 Result: Edited api.py

🔧 Tool: bash
📤 Result: python -c "import api; print('OK')"

✅ Done: Added logging to the API using the logging module...
```

## Configuration Options

Set these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NVIDIA_API_KEY` | *required* | API key |
| `NVIDIA_BASE_URL` | `https://integrate.api.nvidia.com/v1` | API endpoint |
| `NVIDIA_MODEL` | `meta/llama-3.1-405b-instruct` | Model name |

Or use `--api-key`, `--base-url`, `--model` flags.

## Advanced Usage

### Custom System Prompt

Modify `downcode.py` and change the `system_prompt()` method.

### Add New Tools

1. Add tool definition to `system_prompt()`
2. Add execution logic to `execute_tool()` method
3. Done!

### Session Persistence

Sessions currently run fresh each invocation. To add persistence:
- Save conversation history to file
- Load on startup
- Pass previous messages to LLM

## Comparison to Other Tools

| Feature | Downcode | Claude Code | Aider |
|---------|----------|-------------|-------|
| Open-source | ✅ | ❌ | ✅ |
| OpenAI-compatible | ✅ | ❌ | ✅ |
| Multi-provider | ✅ | ❌ | ✅ |
| File context auto-discovery | ✅ | ✅ | ✅ |
| Arbitrary limits | ❌ | 200-line mem cap | Various |
| Language | Python | TypeScript | Python |
| Lines of code | ~200 | ~500K | ~10K |

## License

MIT License - See [LICENSE](LICENSE)

## Contributing

This is a minimal implementation. Contributions welcome:
- Better context management
- Multi-agent coordination
- IDE integrations
- More robust error handling
- Tests (we need tests)

Fork it, modify it, make it yours.

## Roadmap

- [ ] Configuration file support (.downcode.yaml)
- [ ] Interactive mode (chat REPL)
- [ ] Multiple provider support (switch models mid-session)
- [ ] RAG for large codebases
- [ ] Self-modifying capabilities
- [ ] Plugin system
- [ ] Multi-agent coordination

---

**Built in 30 minutes because waiting for permission is slower than building.**
