# LangMentor

A language learning app with a Next.js 16 frontend and a Python/FastAPI backend.

## Quick Start

### 1. Configure API Key

Edit `backend/.env` and set your DashScope API key:
```
DASHSCOPE_API_KEY=your-api-key-here
```

### 2. Start Both Frontend & Backend

```bash
npm run dev:all
```

This starts both services concurrently:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### 3. Access the AI Agent

Open http://localhost:3000/agent to use the AI language learning assistant.

## AI Agent Features

The agent page (`/agent`) has a Windows desktop style UI with 5 tools:

| Tool | Description |
|------|-------------|
| **翻译** | Auto-detect language, translate between Chinese and English |
| **词汇** | Get word definitions, examples, and usage |
| **语法** | Check and correct grammar errors |
| **练习** | Generate language exercises |
| **对话** | Practice conversation with AI tutor |

Double-click desktop icons to open windows. Windows can be dragged, minimized, and closed.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/translate` | POST | Translate text |
| `/api/explain` | POST | Explain a word |
| `/api/grammar` | POST | Check grammar |
| `/api/exercise` | POST | Generate exercises |
| `/api/chat` | POST | Chat with AI tutor |
| `/api/health` | GET | Health check |

## Development

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Next.js dev server |
| `npm run dev:backend` | Start FastAPI backend |
| `npm run dev:all` | Start both frontend and backend |
| `npm run build` | Production build |
| `npm run lint` | Run ESLint |

## Project Structure

```
app/
  agent/              # AI Agent desktop UI
components/
  ui/                 # Reusable UI components (button, window, taskbar, etc.)
  agent/              # Agent feature components
lib/                  # Shared utilities
backend/
  main.py             # FastAPI application
  agent/
    llm.py            # DashScope configuration
    tools.py          # AI Agent tool functions
  .env                # API keys
```

## Tech Stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS v4, shadcn/ui
- **Backend**: Python 3.13+, FastAPI, Pydantic
- **AI**: LangChain, Alibaba DashScope (qwen3.5-plus)
- **Package Managers**: npm (frontend), uv (backend)
