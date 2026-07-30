# Home Orchestrator

A local bilingual family board powered by LangGraph, FastAPI, OpenRouter, and
Groq. Natural-language input becomes an event, task, or note.

一个本地运行的中英双语家庭共享板。自然语言会由 AI 转成日程、待办或笔记。

Events and tasks share one workflow board with personal, owner, type, and text
filters. The calendar supports month and week views; notes stay in a separate
family reference area.

日程和待办进入同一张共享状态板，可按“只看我的”、负责人、类型和文字筛选。
日历支持月视图和周视图；笔记保存在独立的家庭资料区。

## Run / 运行

```powershell
Copy-Item .env.example .env
# Add OPENROUTER_API_KEY and GROQ_API_KEY to .env
uv sync
uv run home-orchestrator
```

Open <http://127.0.0.1:8000>.

Board state is stored in domain tables inside `data/board.sqlite3`. LangGraph
orchestrates AI ingestion and can split one input into multiple items; its
checkpoints are not the board's source of truth. The browser only stores the
selected UI language and current family member.

共享板数据保存在 `data/board.sqlite3`。浏览器只保存界面语言和当前家庭成员。

## Test / 测试

```powershell
uv run python -m unittest -v
```

Tests use a fake AI response and do not call OpenRouter or Groq.
