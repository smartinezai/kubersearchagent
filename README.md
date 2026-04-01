# ☸️ KuberSearch Agent

An AI-powered assistant for searching and querying the official Kubernetes documentation. Ask questions in natural language and get accurate answers with direct links to the source docs.

🌐 **Live app**: [kubersearch.streamlit.app](https://kubersearch.streamlit.app)

---

## Overview

Finding the right information in the Kubernetes documentation can be time-consuming — there are hundreds of pages covering concepts, tasks, reference material and more.

KuberSearch Agent solves this by letting you ask questions in plain English. It searches the official Kubernetes docs, retrieves the most relevant sections, and generates a clear answer with citations linking back to the source material on GitHub.

Built as part of the [AI Agents Crash Course](https://aishippinglabs.com/courses/aihero) by Alexey Grigorev.

---

## Features

- 🔍 **Hybrid search** — combines text and vector search for better retrieval
- 🤖 **AI-powered answers** — uses Llama 3.3 70B via Groq for fast, accurate responses
- 🔗 **Source citations** — every answer includes links to the relevant Kubernetes docs
- 💬 **Web interface** — clean chat UI built with Streamlit
- 🖥️ **CLI interface** — run it from the terminal for quick queries
- 📊 **Evaluation system** — automated LLM-as-a-judge evaluation to measure agent quality

---

## Architecture

```
kubernetes/website (GitHub)
        ↓
   ingest.py          # Downloads and chunks the docs
        ↓
   minsearch Index    # Text search index
        ↓
   search_tools.py    # Search tool for the agent
        ↓
   search_agent.py    # Pydantic AI agent
        ↓
   app.py / main.py   # Streamlit UI / CLI
```

---

## Installation

### Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# Clone the repo
git clone https://github.com/smartinezai/kubersearchagent
cd kubersearchagent/app

# Install dependencies
uv sync

# Set your Groq API key
export GROQ_API_KEY=your-key-here
```

---

## Usage

### Streamlit Web UI

```bash
cd app
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Command Line

```bash
cd app
uv run python main.py
```

Then type your Kubernetes questions at the prompt. Type `stop` to exit.

### Example questions

- *How do I restart a pod?*
- *What is a ConfigMap and how do I use it?*
- *How does a Horizontal Pod Autoscaler work?*
- *What is the difference between a Deployment and a StatefulSet?*

---

## Evaluation

The agent was evaluated using an **LLM-as-a-judge** approach — a separate Groq model automatically scores each response against a checklist of quality criteria.

### Evaluation criteria

| Check | Description |
|---|---|
| `instructions_follow` | Agent followed its system prompt instructions |
| `instructions_avoid` | Agent didn't do anything it was told not to |
| `answer_relevant` | Response directly addresses the question |
| `answer_clear` | Answer is clear and correct |
| `answer_citations` | Response includes proper source citations |
| `completeness` | Answer covers all key aspects of the question |
| `tool_call_search` | Agent used the search tool |

### Results: v2 vs v3 prompt comparison

| Check | v2 (base) | v3 (strict citations) | Difference |
|---|---|---|---|
| instructions_follow | 1.0 | 0.5 | -0.5 |
| instructions_avoid | 1.0 | 1.0 | 0.0 |
| answer_relevant | 1.0 | 0.5 | -0.5 |
| answer_clear | 0.9 | 0.5 | -0.4 |
| answer_citations | 0.9 | 0.5 | -0.4 |
| completeness | 0.9 | 0.5 | -0.4 |
| tool_call_search | 1.0 | 1.0 | 0.0 |

**Key finding**: The v2 prompt performs significantly better. Adding overly strict citation requirements ("every paragraph must have a citation") caused the agent to become too conservative, resulting in incomplete and less relevant answers.

---

## Project Structure

```
kubersearchagent/
├── app/
│   ├── app.py              # Streamlit web interface
│   ├── main.py             # Command-line interface
│   ├── ingest.py           # Data loading and indexing
│   ├── search_tools.py     # Search tool class
│   ├── search_agent.py     # Pydantic AI agent setup
│   ├── logs.py             # Interaction logging
│   └── pyproject.toml      # Dependencies
└── kubernotebook.ipynb     # Development notebook (Days 1-5)
```

---

## Tech Stack

- [Pydantic AI](https://ai.pydantic.dev/) — agent framework
- [Groq](https://groq.com/) — LLM inference (Llama 3.3 70B)
- [minsearch](https://github.com/alexeygrigorev/minsearch) — lightweight search engine
- [Streamlit](https://streamlit.io/) — web interface
- [python-frontmatter](https://github.com/eyeseast/python-frontmatter) — markdown parsing

---

## Acknowledgments

Built following the [AI Agents Crash Course](https://aishippinglabs.com/courses/aihero) by [Alexey Grigorev](https://github.com/alexeygrigorev). The course covers building AI agents from data ingestion to deployment in 7 days.

---

*Made by [smartinezai](https://linkedin.com/in/smartinezai)*