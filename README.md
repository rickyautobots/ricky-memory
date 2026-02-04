# Ricky Memory

[▶️ Watch Demo Video](https://github.com/rickyautobots/ricky-memory/raw/main/evermind_demo.mp4) — EverMemOS Integration

Personal Digital Twin memory system for Ricky, powered by EverMemOS.

## Track

**EverMind Memory Genesis Competition 2026**
- Track 1: Agent + Memory
- Submission: Personal Digital Twin

## What It Does

Bridges Ricky's file-based memory (MEMORY.md, daily logs) with EverMemOS:

1. **Sync** — Import daily logs into EverMemOS
2. **Search** — Semantic search across all memories
3. **Query** — Natural language memory retrieval
4. **Persist** — Long-term memory storage

## Quick Start

```bash
# Start EverMemOS (requires Docker)
cd ../EverMemOS
docker compose up -d

# Test connection
python client.py

# Sync a daily log
python sync.py 2026-02-04
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Ricky Agent   │ ←─► │ RickyMemoryBridge│
│   (OpenClaw)    │     └────────┬────────┘
└─────────────────┘              │
                                 ▼
┌─────────────────┐     ┌─────────────────┐
│   File Memory   │     │    EverMemOS    │
│ (MEMORY.md, etc)│     │  (Vector + KG)  │
└─────────────────┘     └─────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| client.py | EverMemOS API client |
| sync.py | Sync daily logs to EverMemOS |
| query.py | Memory query interface |

## Why This Matters

Current Ricky memory:
- File-based (MEMORY.md, memory/*.md)
- Limited search (grep/text match)
- Manual curation required

With EverMemOS:
- Semantic search (meaning, not keywords)
- Automatic memory extraction
- Scalable storage
- Cross-session context

## Team

- **Ricky** (@rickyautobots) — AI agent
- **Derek** (@zatioj1989) — Human operator
