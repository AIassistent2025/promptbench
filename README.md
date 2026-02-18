# 🎯 PromptBench: Systematic Prompt Engineering Tool

A professional framework for versioning, testing, and automatically evaluating LLM prompts across multiple models.

## 🚀 Overview
PromptBench is designed for AI Engineers and Prompt Specialists who need to ensure model reliability and response quality. It automates the benchmarking process, providing scoring based on structural integrity (JSON), relevance, and efficiency.

## ✨ Key Features
- **Multi-Model Support:** Run benchmarks across GPT-4, Claude, Llama 3, and Gemini via a unified API.
- **Automated Scoring:** Heuristic-based evaluation (Length, Keyword density, JSON validatity).
- **Versioning:** Prompts are stored as YAML templates for easy iteration and tracking.
- **Performance Metrics:** Real-time tracking of latency and token consumption.

## 🛠 Installation
```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY='your_key_here'
```

## 📊 Usage
Run a benchmark on a specific prompt template:
```bash
python main.py prompts/sample_task.yaml
```

## 📂 Project Structure
- `core/`: Evaluation and API logic.
- `prompts/`: Versioned prompt templates.
- `config.yaml`: Model selection and configuration.
