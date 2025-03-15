# Adaptive Phishing Awareness Training

An interactive phsihing simulation that utilizes LLMs for generating messages, adapted to specific users and environments, and for coaching users. The simulation is based on Flask and requires the setup of an LLM-API to a local LLM via <a href="https://ollama.com/">Ollama</a> or the "<a href="https://llm.datasette.io/en/stable/">llm</a>" library. By default, the qwen 2.5 7B LLM is configured via Ollama.

[![IMAGE ALT TEXT HERE](https://raw.githubusercontent.com/fhaer/adaptive-phishing-awareness-training/main/Video.png)](https://www.youtube.com/watch?v=UUYAv6r7agY)

---

## Installation and Usage

### 1. Project Setup
- Python 3.13 or later is required
- Setup of a virtual environment in the project directory:
  - **macOS/Linux:**
    ```bash
      python3 -m venv .venv
      source .venv/bin/activate
    ```
  - **Windows:**
    ```bash
      python -m venv .venv
      .venv\Scripts\Activate
    ```
- Installation of required libraries:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Launch
- Start the application:
  ```bash
  python app.py
  ```
- By default, the web-based UI is available at <a href="http://127.0.0.1:8081/">http://127.0.0.1:8081/</a>.
