# Adaptive Phishing Awareness Training

An interactive phishing simulation that utilizes LLMs for generating messages, adapted to specific users and environments, and for coaching users. The simulation requires the setup of an LLM-API to a local LLM via <a href="https://ollama.com/">Ollama</a> or the "<a href="https://llm.datasette.io/en/stable/">llm</a>" library. By default, the qwen 2.5 7B LLM is configured via Ollama.

**Example**: After flagging a phishing message as a legitimate message, the behavior of the LLM can be observed, giving feedback (1) and answering questions (2, 3). Qwen 2.5 7B is used in the example.

![UI-2](https://raw.githubusercontent.com/fhaer/adaptive-phishing-awareness-training/main/UI-2.png)

**Video**: <a href="https://www.youtube.com/watch?v=UUYAv6r7agY">Watch on YouTube</a>

---

The prototype is implemented in Python 3.13 using the modules flask, flask-cors, ollama, llm, and openai. Parts of the HTML/JS/CSS code are derived from the <a href="https://github.com/patrickloeber/chatbot-deployment">chatbot-deployment</a> project.
 
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
- LLM
  - Start Ollama or configure another LLM-API in llm_api.py
  - By default, the qwen 2.5 7B LLM is set
  - Model download:
     ```bash
     ollama pull qwen2.5:7b
     ```
- Start the application:
  ```bash
  python app.py
  ```
- By default, the web-based UI is available at <a href="http://127.0.0.1:8081/">http://127.0.0.1:8081/</a>.
