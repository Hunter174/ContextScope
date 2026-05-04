# ContextScope

ContextScope is a desktop application designed to automatically capture, structure, and retrieve contextual information from a user’s screen. It integrates real-time OCR, vector search, and LLM-based reasoning to eliminate manual context transfer in workflows such as messaging, coding, and task management.

---

## Overview

ContextScope operates in two primary modes:

- **Manual Mode**: Capture a single screen region and send it to the LLM
- **Streaming Mode**: Continuously extract text from a defined region and build a searchable context store

The system enables:
- Real-time transcription of on-screen content
- Structured storage of extracted text
- Retrieval-augmented LLM interactions
- Optional integration with external tools (e.g., Jira)

---

## Features

- PyQt-based overlay UI (non-intrusive, always-on-top windows)
- Region-based screen capture
- Streaming OCR using Amazon Textract
- Context chunking and indexing via FAISS
- Retrieval-Augmented Generation (RAG)
- Structured JSON LLM responses
- Extensible tool system for automation (e.g., task creation)

---

## Architecture

```
ContextScope
│
├── app/
│   └── main.py
│
├── core/
│   ├── app_controller.py
│   ├── llm_client.py
│   ├── capture_service.py
│   ├── stream_worker.py
│   ├── ocr/
│   └── vector_store/
│
├── ui/
│   ├── chat_window.py
│   ├── capture_window.py
│   └── text_window.py
│
├── prompts/
│   └── general_prompt.j2
│
├── docs/
│   └── ContextScope_Technical_Report.docx
│
└── README.md
```

---

## System Components

### GUI (PyQt)
- **Chat Window**: Main control interface for user interaction
- **Capture Window**: Defines region for context extraction
- **Text Window**: Displays accumulated context

### Capture Pipeline
1. Screen region captured via `QScreen.grabWindow`
2. Frame deduplicated using hash comparison
3. OCR applied (Textract)
4. Text chunked (~300 chars)
5. Stored in FAISS vector database

### Streaming Behavior
- Interval-based capture (default ~500ms)
- OCR cooldown (~2s)
- Deduplication to prevent redundant processing
- Final buffer flush to FAISS on stream termination

### LLM Integration
- Jinja2-based prompt templating
- Strict JSON output format:
```
{
  "response": "...",
  "notepad": "..."
}
```

---

## Installation

```
git clone https://github.com/yourusername/contextscope.git
cd contextscope

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
```

---

## Usage

```
python app/main.py
```

### Controls
- Toggle capture mode (manual / streaming)
- Define capture region
- Start/stop streaming (acts as toggle)
- Send prompt to LLM with accumulated context

---

## Technical Report

The full technical report for this project is available here:

👉 [ContextScope Technical Report](./docs/ContextScope_Technical_Report.docx)

---

## Configuration

Key configurable components:

- **Streaming interval**: `ContextStreamWorker(interval_ms)`
- **OCR backend**: Textract (default), extensible to other engines
- **Vector store**: FAISS
- **Prompt templates**: `/prompts/*.j2`

---

## Roadmap

- Improve real-time OCR latency
- Add structured entity extraction (e.g., "user: message")
- Enhance multi-window tracking
- Add cloud sync for context storage
- Expand tool registry (Jira, Slack, etc.)

---

## Contributing

1. Fork the repository  
2. Create a feature branch  
3. Submit a pull request  

---

## License

MIT License (or specify your choice)

---

## Notes on Linking `.docx`

The relative link used:
```
./docs/ContextScope_Technical_Report.docx
```
works because:
- GitHub renders it as a downloadable file
- It remains valid across branches unless path changes

Optional preview link:
```
https://docs.google.com/viewer?url=https://raw.githubusercontent.com/<user>/<repo>/main/docs/ContextScope_Technical_Report.docx
```
```
