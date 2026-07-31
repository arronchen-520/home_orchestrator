# Home Orchestrator

A local bilingual family board built with LangGraph, FastAPI, OpenRouter, and
Groq. Type or speak in Chinese or English to add events, tasks, and notes.

The intake assistant asks up to two questions when important details are
missing. Before saving, it shows schedule conflicts and lets you review each
item, change or clear the suggested owner, and accept or reject a suggested
preparation.

The family assistant in the bottom-right answers questions about schedules,
tasks, reminders, preparations, and notes. It can suggest one item update for
you to confirm. Its AI-generated SQL runs only against a household-scoped
read-only snapshot.

这是一个本地运行的中英双语家庭共享板。输入文字或说一句话，就能添加日程、
待办和笔记。

Events and tasks share one board with filters for member, owner, type, and
text. The calendar has month and week views. Notes have their own section.

日程和待办放在同一张看板里，可按“只看我的”、负责人、类型和文字筛选。
日历有月视图和周视图，笔记放在单独的页面。

## Run / 运行

```powershell
Copy-Item .env.example .env
# Add OPENROUTER_API_KEY, GROQ_API_KEY, and OPENWEATHER_API_KEY to .env
uv sync
uv run home-orchestrator
```

Open <http://127.0.0.1:8000>.

Board data is stored in domain tables inside `data/board.sqlite3`. LangGraph
handles AI input and can split one input into multiple items. Its checkpoints
are not the board's source of truth. The browser only stores the selected UI
language and current family member.

On first launch, enter the household city, for example `Toronto, CA`.
OpenWeather finds and saves the location, then shows a cached five-day
forecast in Calendar.

共享板数据保存在 `data/board.sqlite3`。浏览器只保存界面语言和当前家庭成员。

## Test / 测试

```powershell
uv run python -m unittest -v
```

Tests use a fake AI response and do not call OpenRouter or Groq.
